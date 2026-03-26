import requests
import logging
import json
from bot.config import POLLINATIONS_API_KEY, POLLINATIONS_ENABLED

logger = logging.getLogger(__name__)

class PollinationsClient:
    def __init__(self):
        self.api_key = POLLINATIONS_API_KEY
        self.enabled = POLLINATIONS_ENABLED and bool(self.api_key)
        self.base_url = "https://gen.pollinations.ai"

    def generate_image(self, prompt):
        """
        Генерирует изображение по текстовому запросу через Pollinations.ai API
        Возвращает bytes изображения или None
        """
        if not self.enabled:
            logger.warning("Pollinations is disabled or no API key")
            return None

        try:
            # Формируем запрос к API
            url = f"{self.base_url}/image/{prompt.replace(' ', '_')}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Generating image for prompt: {prompt[:50]}...")

            response = requests.get(
                url,
                headers=headers,
                timeout=45,
                params={
                    "width": 1024,
                    "height": 1024,
                    "model": "flux"
                }
            )

            if response.status_code == 200:
                content = response.content
                if len(content) > 1000 and content[:2] == b'\xff\xd8':
                    logger.info(f"Image generated, size: {len(content)} bytes")
                    return content
                else:
                    logger.warning(f"Response not an image, status: {response.status_code}, size: {len(content)}")
                    return None
            else:
                logger.error(f"API error: {response.status_code}, {response.text[:200]}")
                return None

        except requests.exceptions.Timeout:
            logger.error("Pollinations request timeout")
            return None
        except Exception as e:
            logger.error(f"Pollinations error: {e}")
            return None

    def generate_image_with_fallback(self, topic):
        """Генерирует изображение с улучшенным промптом"""
        prompts = [
            f"high quality photorealistic {topic}",
            f"beautiful realistic {topic}",
            f"{topic} photography"
        ]

        for prompt in prompts:
            logger.info(f"Trying prompt: {prompt}")
            result = self.generate_image(prompt)
            if result:
                return result
        return None

    def generate_image_russian(self, topic):
        """Генерирует изображение с русскоязычным промптом"""
        prompts = [
            f"фотореалистичное качественное изображение {topic}",
            f"красивое реалистичное фото {topic}",
            topic
        ]

        for prompt in prompts:
            logger.info(f"Trying Russian prompt: {prompt}")
            result = self.generate_image(prompt)
            if result:
                return result
        return None