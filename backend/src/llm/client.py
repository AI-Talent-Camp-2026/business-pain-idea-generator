import httpx
import asyncio
from typing import Optional, Dict, Any
from ..config import settings, logger


class OpenRouterClient:
    """Client for OpenRouter API"""

    def __init__(self):
        self.base_url = settings.openrouter_base_url
        self.api_key = settings.openrouter_api_key
        self.model = "anthropic/claude-3.5-sonnet"  # Default model

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """Generate text using OpenRouter API"""

        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://pain-to-idea-generator.app",  # Optional
            "X-Title": "Pain-to-Idea Generator"  # Optional
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # Log request details
        logger.info(f"OpenRouter Request:")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  Temperature: {temperature}")
        logger.info(f"  Max tokens: {max_tokens}")
        logger.info(f"  System prompt length: {len(system_prompt) if system_prompt else 0} chars")
        logger.info(f"  User prompt length: {len(prompt)} chars")
        logger.info(f"  User prompt preview: {prompt[:200]}...")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                # Log response details
                content = data['choices'][0]['message']['content']
                logger.info(f"OpenRouter Response:")
                logger.info(f"  Status: {response.status_code}")
                logger.info(f"  Content length: {len(content)} chars")
                logger.info(f"  Content preview: {content[:500]}...")
                if 'usage' in data:
                    logger.info(f"  Token usage: {data['usage']}")

                return content

        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter API error: {e.response.text}")
            raise Exception(f"Ошибка OpenRouter API: {e.response.status_code}")
        except Exception as e:
            logger.error(f"OpenRouter client error: {e}")
            raise Exception(f"Ошибка генерации: {str(e)}")


# Singleton instance
llm_client = OpenRouterClient()
