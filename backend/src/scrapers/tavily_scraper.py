"""
Tavily Search API integration for finding real user pains
"""
import httpx
from typing import List, Dict, Optional
from ..config import settings, logger


class TavilyScraper:
    """
    Scraper using Tavily Search API to find real user pain discussions
    across the internet (Reddit, forums, blogs, etc.)
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.tavily_api_key
        self.base_url = "https://api.tavily.com/search"

        if not self.api_key:
            raise ValueError("Tavily API key not configured")

    async def search_pains(self, direction: str, max_results: int = 10) -> List[Dict]:
        """
        Search for real user pain discussions related to the business direction

        Args:
            direction: Business direction (e.g., "B2B SaaS для стартапов")
            max_results: Maximum number of results to return (default: 10)

        Returns:
            List of search results with pain-related content:
            [
                {
                    "title": "...",
                    "url": "...",
                    "content": "...",
                    "score": 0.95,
                    "source": "reddit.com"
                },
                ...
            ]
        """
        logger.info(f"[Tavily] Searching for pains in direction: {direction}")

        # Build search queries focused on finding problems/pains
        queries = self._build_pain_queries(direction)

        all_results = []

        for query in queries:
            try:
                results = await self._search(query, max_results=max_results)
                all_results.extend(results)
                logger.info(f"[Tavily] Query '{query}' returned {len(results)} results")
            except Exception as e:
                logger.error(f"[Tavily] Error searching for '{query}': {e}")
                continue

        # Remove duplicates by URL
        unique_results = self._deduplicate_by_url(all_results)

        logger.info(f"[Tavily] Total unique results: {len(unique_results)}")
        return unique_results[:max_results * 2]  # Return up to 2x max_results across all queries

    def _build_pain_queries(self, direction: str) -> List[str]:
        """
        Build search queries optimized for finding user pains

        Args:
            direction: Business direction

        Returns:
            List of search queries
        """
        # Extract key terms from direction
        key_terms = self._extract_key_terms(direction)

        # Build queries with pain-focused keywords
        pain_keywords = [
            "problem struggle pain",
            "frustrating annoying difficult",
            "hate worst issue",
            "complaint need solution",
            "looking for tool help"
        ]

        queries = []
        for pain_kw in pain_keywords[:3]:  # Use top 3 pain keyword sets
            query = f"{key_terms} {pain_kw} site:reddit.com OR site:indiehackers.com"
            queries.append(query)

        return queries

    def _extract_key_terms(self, direction: str) -> str:
        """
        Extract key terms from business direction

        Args:
            direction: Business direction text

        Returns:
            Key terms string
        """
        # Simple extraction - take first 3-4 meaningful words
        words = direction.lower().split()
        # Filter out common words
        stop_words = {'для', 'и', 'в', 'на', 'с', 'по', 'или', 'the', 'and', 'or', 'for'}
        key_words = [w for w in words if w not in stop_words][:4]
        return ' '.join(key_words)

    async def _search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Execute Tavily search API call

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of search results
        """
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",  # More comprehensive search
            "max_results": max_results,
            "include_answer": False,  # We don't need AI-generated answer
            "include_raw_content": False,  # We only need snippets
            "include_domains": [
                "reddit.com",
                "indiehackers.com",
                "news.ycombinator.com",
                "producthunt.com"
            ]
        }

        logger.info(f"[Tavily] Sending search request:")
        logger.info(f"  Query: {query}")
        logger.info(f"  Max results: {max_results}")
        logger.info(f"  Domains: {', '.join(payload['include_domains'])}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                # Extract results
                results = []
                for idx, result in enumerate(data.get('results', []), 1):
                    result_data = {
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'content': result.get('content', ''),
                        'score': result.get('score', 0.0),
                        'source': self._extract_domain(result.get('url', ''))
                    }
                    results.append(result_data)

                    # Log each result for debugging
                    logger.info(f"[Tavily] Result {idx}/{len(data.get('results', []))}:")
                    logger.info(f"  Source: {result_data['source']}")
                    logger.info(f"  Title: {result_data['title'][:100]}")
                    logger.info(f"  URL: {result_data['url']}")
                    logger.info(f"  Content preview: {result_data['content'][:200]}...")

                return results

        except httpx.HTTPStatusError as e:
            logger.error(f"[Tavily] API error: {e.response.text}")
            raise Exception(f"Tavily API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"[Tavily] Client error: {e}")
            raise Exception(f"Tavily search error: {str(e)}")

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return 'unknown'

    def _deduplicate_by_url(self, results: List[Dict]) -> List[Dict]:
        """
        Remove duplicate results by URL

        Args:
            results: List of search results

        Returns:
            Deduplicated list
        """
        seen_urls = set()
        unique = []

        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(result)

        return unique
