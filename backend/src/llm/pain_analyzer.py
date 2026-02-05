"""
Pain Analyzer - extracts structured pain data from raw search results
"""
import json
from typing import List, Dict, Any
from .client import llm_client
from ..config import logger


class PainAnalyzer:
    """
    Analyzes raw search results and extracts structured user pains
    """

    def __init__(self, llm_client_instance=None):
        self.llm = llm_client_instance or llm_client

    async def extract_pains(self, search_results: List[Dict], direction: str) -> List[Dict]:
        """
        Extract structured pain data from search results

        Args:
            search_results: List of Tavily search results
            direction: Business direction context

        Returns:
            List of structured pains:
            [
                {
                    "pain_description": "Описание боли",
                    "segment": "Целевая аудитория",
                    "evidence": [
                        {"source": "url", "quote": "цитата"}
                    ],
                    "confidence_level": "high|medium|low"
                },
                ...
            ]
        """
        if not search_results:
            logger.warning("[PainAnalyzer] No search results to analyze")
            return []

        logger.info(f"[PainAnalyzer] Analyzing {len(search_results)} search results")

        # Group results into batches to avoid token limits
        batch_size = 15
        batches = [search_results[i:i+batch_size] for i in range(0, len(search_results), batch_size)]

        all_pains = []

        for idx, batch in enumerate(batches):
            logger.info(f"[PainAnalyzer] Processing batch {idx+1}/{len(batches)}")
            try:
                pains_batch = await self._analyze_batch(batch, direction)
                all_pains.extend(pains_batch)
            except Exception as e:
                logger.error(f"[PainAnalyzer] Error processing batch {idx+1}: {e}")
                continue

        # Cluster similar pains
        clustered_pains = self._cluster_similar_pains(all_pains)

        logger.info(f"[PainAnalyzer] Extracted {len(clustered_pains)} unique pains")
        return clustered_pains

    async def _analyze_batch(self, batch: List[Dict], direction: str) -> List[Dict]:
        """
        Analyze a batch of search results

        Args:
            batch: Batch of search results
            direction: Business direction

        Returns:
            List of extracted pains
        """
        # Build context from search results
        context = self._build_context(batch)

        # Create analysis prompt
        prompt = f"""Ты анализируешь реальные обсуждения пользователей из интернета (Reddit, Indie Hackers, форумы).

Направление бизнеса: {direction}

Реальные обсуждения пользователей:
{context}

Задача: Извлеки из этих обсуждений КОНКРЕТНЫЕ боли и проблемы пользователей.

Требования:
1. Боль должна быть КОНКРЕТНОЙ (не "плохой UX", а "приходится кликать 10 раз чтобы...")
2. Боль должна относиться к направлению: {direction}
3. Для каждой боли укажи доказательства (цитаты из текста)
4. Уровень уверенности зависит от количества и качества доказательств

Верни JSON массив:
[
  {{
    "pain_description": "Конкретное описание боли (100-200 слов)",
    "segment": "Кому именно болит (целевая аудитория)",
    "evidence_quotes": ["цитата 1 из реального обсуждения", "цитата 2"],
    "confidence_level": "high|medium|low"
  }}
]

ВАЖНО:
- Если в обсуждениях нет явных болей - верни пустой массив []
- Не придумывай боли - только то что явно написано в обсуждениях
- Одна боль = одна конкретная проблема

Только JSON, без комментариев."""

        try:
            response_text = await self.llm.generate(
                prompt=prompt,
                system_prompt="Ты эксперт по анализу пользовательских болей. Ты извлекаешь структурированные данные из сырых текстов.",
                temperature=0.3,  # Lower temperature for more consistent extraction
                max_tokens=4000
            )

            # Parse JSON response
            response_text = response_text.strip()
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])

            pains = json.loads(response_text)

            if not isinstance(pains, list):
                logger.warning("[PainAnalyzer] Response is not a list, trying to extract")
                pains = pains.get('pains', [])

            return pains

        except json.JSONDecodeError as e:
            logger.error(f"[PainAnalyzer] Failed to parse JSON: {e}")
            logger.error(f"[PainAnalyzer] Response: {response_text[:500]}")
            return []
        except Exception as e:
            logger.error(f"[PainAnalyzer] Error in analysis: {e}")
            return []

    def _build_context(self, batch: List[Dict]) -> str:
        """
        Build context string from search results

        Args:
            batch: Batch of search results

        Returns:
            Formatted context string
        """
        context_parts = []

        for idx, result in enumerate(batch, 1):
            title = result.get('title', '')
            content = result.get('content', '')
            url = result.get('url', '')
            source = result.get('source', '')

            context_parts.append(f"""
--- Обсуждение {idx} [{source}] ---
Заголовок: {title}
URL: {url}
Текст: {content}
""")

        return '\n'.join(context_parts)

    def _cluster_similar_pains(self, pains: List[Dict]) -> List[Dict]:
        """
        Cluster similar pains together and merge evidence

        Args:
            pains: List of extracted pains

        Returns:
            Clustered pains with merged evidence
        """
        if len(pains) <= 1:
            return pains

        # Simple clustering by pain description similarity
        # For MVP, we'll just deduplicate exact matches
        # TODO: Implement semantic similarity clustering

        clustered = {}

        for pain in pains:
            pain_desc = pain.get('pain_description', '')
            key = pain_desc[:100].lower()  # Use first 100 chars as key

            if key in clustered:
                # Merge evidence
                existing_quotes = clustered[key].get('evidence_quotes', [])
                new_quotes = pain.get('evidence_quotes', [])
                clustered[key]['evidence_quotes'] = list(set(existing_quotes + new_quotes))

                # Upgrade confidence if we have more evidence
                if len(clustered[key]['evidence_quotes']) > 3:
                    clustered[key]['confidence_level'] = 'high'
            else:
                clustered[key] = pain

        return list(clustered.values())
