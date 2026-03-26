import requests
import logging
import random
from bot.config import POLLINATIONS_API_KEY, POLLINATIONS_ENABLED

logger = logging.getLogger(__name__)

class PollinationsClient:
    def __init__(self):
        self.api_key = POLLINATIONS_API_KEY
        self.enabled = POLLINATIONS_ENABLED and bool(self.api_key)

    def generate_image(self, prompt):
        if not self.enabled:
            return None
        try:
            seed = random.randint(1, 999999)
            encoded_prompt = prompt.replace(" ", "_")[:100]
            url = f"https://pollinations.ai/p/{encoded_prompt}"
            params = {"width": 1024, "height": 1024, "seed": seed, "model": "flux"}
            response = requests.get(url, params=params, timeout=60)
            if response.status_code == 200 and response.content and len(response.content) > 1000:
                return response.content
        except Exception as e:
            logger.error(f"Pollinations error: {e}")
        return None

    def generate_image_variations(self, topic):
        prompts = [
            f"{topic} beautiful photo",
            f"amazing {topic}",
            f"stunning {topic} photography"
        ]
        return self.generate_image(random.choice(prompts))

    def generate_image_with_fallback(self, topic):
        return self.generate_image_variations(topic)

    def generate_image_russian(self, topic):
        prompts = [
            f"{topic} красивое фото",
            f"фото {topic}",
            f"изображение {topic}"
        ]
        return self.generate_image(random.choice(prompts))