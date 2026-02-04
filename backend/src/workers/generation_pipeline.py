"""
Idea generation pipeline

This worker generates business ideas using OpenRouter LLM
"""
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any

from ..models import SessionLocal, Run, Idea, Analogue
from ..llm.client import llm_client
from ..llm.prompts import get_generate_ideas_prompt, SYSTEM_PROMPT
from ..config import logger


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
        run.current_stage = 'Поиск идей'
        db.commit()

        # Generate ideas using LLM
        prompt, selected_direction = get_generate_ideas_prompt(run.optional_direction or "")

        # Save selected direction
        run.selected_direction = selected_direction
        db.commit()

        logger.info(f"Calling OpenRouter API for run {run_id} with direction: {selected_direction}")

        # Use asyncio to call async LLM client
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response_text = loop.run_until_complete(
            llm_client.generate(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=8000
            )
        )
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

                # Create idea
                idea = Idea(
                    run_id=run_id,
                    title=idea_data['title'][:200],  # Truncate to 200 chars
                    pain_description=idea_data['pain_description'],
                    segment=idea_data['segment'][:200],
                    confidence_level=idea_data.get('confidence_level', 'medium').lower(),
                    brief_evidence=idea_data.get('brief_evidence', 'Доказательства анализируются...'),
                    plan_7days=idea_data.get('plan_7days', 'План генерируется...'),
                    plan_30days=idea_data.get('plan_30days', 'План генерируется...'),
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
        if saved_count < 10:
            raise Exception(f"Недостаточно идей сгенерировано: {saved_count} (требуется минимум 10)")

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
