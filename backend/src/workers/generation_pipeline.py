"""
Idea generation pipeline

This worker generates business ideas using OpenRouter LLM
with REAL user pain data from Tavily Search
"""
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any

from ..models import SessionLocal, Run, Idea, Analogue
from ..llm.client import llm_client
from ..llm.prompts import (
    get_generate_ideas_prompt,
    get_generate_ideas_from_real_pains_prompt,
    SYSTEM_PROMPT
)
from ..scrapers.tavily_scraper import TavilyScraper
from ..llm.pain_analyzer import PainAnalyzer
from ..config import logger, settings


def generate_ideas(run_id: str):
    """
    Main generation pipeline for creating business ideas

    This function runs as a background job in RQ worker
    """
    db = SessionLocal()

    try:
        # Get run
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            logger.error(f"Run {run_id} not found")
            return

        logger.info(f"Starting generation for run {run_id}")

        # Update status
        run.status = 'running'
        db.commit()

        # Setup asyncio loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Determine direction
            _, selected_direction = get_generate_ideas_prompt(run.optional_direction or "")
            run.selected_direction = selected_direction
            db.commit()

            logger.info(f"Selected direction for run {run_id}: {selected_direction}")

            # STAGE 1: Search for real user pains using Tavily
            run.current_stage = 'Поиск реальных болей пользователей'
            db.commit()

            logger.info(f"[Stage 1] Searching for real pains via Tavily...")

            try:
                tavily_scraper = TavilyScraper()
                search_results = loop.run_until_complete(
                    tavily_scraper.search_pains(selected_direction, max_results=10)
                )
                logger.info(f"[Stage 1] Found {len(search_results)} search results from Tavily")
            except Exception as e:
                logger.warning(f"[Stage 1] Tavily search failed: {e}. Falling back to LLM-only generation")
                search_results = []

            # STAGE 2: Analyze and extract structured pains
            real_pains = []
            if search_results:
                run.current_stage = 'Анализ найденных болей'
                db.commit()

                logger.info(f"[Stage 2] Analyzing search results to extract pains...")

                try:
                    pain_analyzer = PainAnalyzer(llm_client)
                    real_pains = loop.run_until_complete(
                        pain_analyzer.extract_pains(search_results, selected_direction)
                    )
                    logger.info(f"[Stage 2] Extracted {len(real_pains)} structured pains")
                except Exception as e:
                    logger.error(f"[Stage 2] Pain analysis failed: {e}")
                    real_pains = []

            # STAGE 3: Generate ideas
            run.current_stage = 'Генерация бизнес-идей'
            db.commit()

            logger.info(f"[Stage 3] Generating ideas...")

            # Choose prompt based on whether we have real pains
            if real_pains and len(real_pains) >= 3:
                logger.info(f"[Stage 3] Using REAL PAINS mode with {len(real_pains)} pains")
                prompt = get_generate_ideas_from_real_pains_prompt(selected_direction, real_pains)
            else:
                logger.info(f"[Stage 3] Falling back to LLM-only mode (not enough real pains)")
                prompt, _ = get_generate_ideas_prompt(selected_direction)

            response_text = loop.run_until_complete(
                llm_client.generate(
                    prompt=prompt,
                    system_prompt=SYSTEM_PROMPT,
                    temperature=0.7,
                    max_tokens=8000
                )
            )

        finally:
            loop.close()

        logger.info(f"Received response from OpenRouter for run {run_id}")

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            response_text = response_text.strip()
            if response_text.startswith('```'):
                # Remove markdown code block markers
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])

            ideas_data = json.loads(response_text)

            if not isinstance(ideas_data, list):
                # Handle {"ideas": [...]} format
                ideas_data = ideas_data.get('ideas', [])

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            raise Exception(f"Ошибка парсинга ответа LLM: {str(e)}")

        # Update stage
        run.current_stage = 'Сохранение результатов'
        db.commit()

        # Save ideas to database
        saved_count = 0
        for idx, idea_data in enumerate(ideas_data[:15]):  # Limit to 15 ideas
            try:
                # Validate required fields
                required_fields = ['title', 'pain_description', 'segment', 'confidence_level']
                if not all(field in idea_data for field in required_fields):
                    logger.warning(f"Skipping idea {idx}: missing required fields")
                    continue

                # Convert plans from list to string if needed
                plan_7days = idea_data.get('plan_7days', 'План генерируется...')
                if isinstance(plan_7days, list):
                    plan_7days = '\n'.join(f"- {step}" for step in plan_7days)

                plan_30days = idea_data.get('plan_30days', 'План генерируется...')
                if isinstance(plan_30days, list):
                    plan_30days = '\n'.join(f"- {step}" for step in plan_30days)

                # Create idea
                idea = Idea(
                    run_id=run_id,
                    title=idea_data['title'][:200],  # Truncate to 200 chars
                    pain_description=idea_data['pain_description'],
                    segment=idea_data['segment'][:200],
                    confidence_level=idea_data.get('confidence_level', 'medium').lower(),
                    brief_evidence=idea_data.get('brief_evidence', 'Доказательства анализируются...'),
                    plan_7days=plan_7days,
                    plan_30days=plan_30days,
                    order_index=idx
                )

                db.add(idea)
                db.flush()  # Get idea.id

                # Add analogues
                analogues_data = idea_data.get('analogues', [])
                for aidx, analogue_data in enumerate(analogues_data[:3]):  # Max 3 analogues
                    try:
                        analogue = Analogue(
                            idea_id=idea.id,
                            name=analogue_data.get('name', 'Аналог')[:200],
                            description=analogue_data.get('description', 'Описание недоступно'),
                            url=analogue_data.get('url', 'https://example.com')[:500],
                            order_index=aidx
                        )
                        db.add(analogue)
                    except Exception as e:
                        logger.warning(f"Failed to add analogue {aidx} for idea {idea.id}: {e}")

                saved_count += 1

            except Exception as e:
                logger.error(f"Failed to save idea {idx}: {e}")
                continue

        # Validate we have enough ideas
        if saved_count < 3:
            raise Exception(f"Недостаточно идей сгенерировано: {saved_count} (требуется минимум 3)")

        # Mark run as completed
        run.status = 'completed'
        run.completed_at = datetime.utcnow()
        run.ideas_count = saved_count
        run.current_stage = 'Завершено'
        db.commit()

        logger.info(f"Successfully completed run {run_id} with {saved_count} ideas")

    except Exception as e:
        logger.error(f"Error in generation pipeline for run {run_id}: {e}")

        # Mark run as failed
        run.status = 'failed'
        run.error_message = f"Ошибка генерации: {str(e)}"
        db.commit()

        raise

    finally:
        db.close()
