import requests
import logging
from bot.config import POLLINATIONS_ENABLED

logger = logging.getLogger(__name__)

class PollinationsClient:
    def __init__(self):
        self.base_url = "https://image.pollinations.ai/prompt/"
        self.enabled = POLLINATIONS_ENABLED

    def generate_image(self, prompt):
        """
        Генерирует изображение по текстовому запросу
        Возвращает bytes изображения или None
        """
        if not self.enabled:
            return None

        try:
            # Экранируем пробелы и спецсимволы
            prompt_encoded = prompt.replace(" ", "%20").replace("?", "").replace("!", "")
            url = f"{self.base_url}{prompt_encoded}"
            logger.info(f"Generating image for prompt: {prompt[:50]}...")

            response = requests.get(url, timeout=45)

            if response.status_code == 200 and response.content:
                # Проверяем, что это действительно изображение
                if response.content[:4] in [b'\xff\xd8\xff\xe0', b'\x89PNG']:
                    logger.info(f"Image generated successfully, size: {len(response.content)} bytes")
                    return response.content
                else:
                    logger.warning(f"Response is not an image, first bytes: {response.content[:10]}")
                    return None
            else:
                logger.error(f"Failed to generate image: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            logger.error("Pollinations request timeout")
            return None
        except Exception as e:
            logger.error(f"Pollinations error: {e}")
            return None

    def generate_image_with_fallback(self, topic):
        """
        Генерирует изображение с улучшенным промптом
        """
        prompt = f"Photorealistic high quality detailed image: {topic}"
        return self.generate_image(prompt)

    def generate_image_russian(self, topic):
        """
        Генерирует изображение с русскоязычным промптом
        """
        prompt = f"Фотореалистичное качественное детальное изображение: {topic}"
        return self.generate_image(prompt)