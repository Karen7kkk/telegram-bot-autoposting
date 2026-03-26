import requests
import logging
import random
import time
from bot.config import POLLINATIONS_API_KEY, POLLINATIONS_ENABLED

logger = logging.getLogger(__name__)

class PollinationsClient:
    def __init__(self):
        self.api_key = POLLINATIONS_API_KEY
        self.enabled = POLLINATIONS_ENABLED and bool(self.api_key)

    def generate_image(self, prompt):
        """
        Генерирует изображение по текстовому запросу
        Добавляет случайные параметры для разнообразия
        """
        if not self.enabled:
            return None

        try:
            # Случайный seed для разнообразия
            seed = random.randint(1, 999999)
            # Случайный размер
            width = random.choice([1024, 1024, 1024, 768, 1200])
            height = random.choice([1024, 1024, 1024, 768, 1200])

            # Формируем URL с параметрами
            encoded_prompt = prompt.replace(" ", "_").replace("?", "").replace("!", "")
            url = f"https://pollinations.ai/p/{encoded_prompt}"

            params = {
                "width": width,
                "height": height,
                "seed": seed,
                "model": "flux",
                "nologo": "true"
            }

            logger.info(f"Generating image with seed={seed}, size={width}x{height}")

            response = requests.get(url, params=params, timeout=60)

            if response.status_code == 200 and response.content:
                content = response.content
                if len(content) > 1000 and content[:2] == b'\xff\xd8':
                    logger.info(f"Image generated, size: {len(content)} bytes")
                    return content
            return None

        except Exception as e:
            logger.error(f"Pollinations error: {e}")
            return None

    def generate_image_variations(self, topic):
        """
        Генерирует изображение с вариациями промпта
        """
        # Список разных промптов для разнообразия
        prompts = [
            f"фотореалистичное качественное изображение {topic}, детали, красивое освещение",
            f"красивое реалистичное фото {topic}, профессиональная фотография",
            f"{topic}, высокое качество, детали",
            f"удивительное фото {topic}, художественное",
            f"{topic}, стильная композиция, четкое изображение",
            f"профессиональное фото {topic}, хорошее освещение",
            f"{topic} в высоком разрешении, детали"
        ]

        # Добавляем случайные слова для разнообразия
        adjectives = ["красивый", "удивительный", "стильный", "эффектный", "яркий", "атмосферный"]
        if random.random() > 0.5:
            adj = random.choice(adjectives)
            prompts.append(f"{adj} {topic}, качественное фото")

        # Случайно выбираем промпт
        selected_prompt = random.choice(prompts)
        logger.info(f"Selected prompt: {selected_prompt}")

        return self.generate_image(selected_prompt)

    def generate_image_russian(self, topic):
        """Генерирует изображение с русскоязычным промптом и вариациями"""
        return self.generate_image_variations(topic)

    def generate_image_with_fallback(self, topic):
        """Генерирует изображение с английским промптом"""
        prompts = [
            f"high quality photorealistic {topic}, detailed",
            f"beautiful realistic {topic}, professional photography",
            f"{topic}, high resolution, details",
            f"amazing {topic} photography"
        ]
        selected_prompt = random.choice(prompts)
        return self.generate_image(selected_prompt)