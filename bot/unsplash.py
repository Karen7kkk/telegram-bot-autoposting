import random
import requests
import logging
from bot.config import UNSPLASH_ACCESS_KEY

logger = logging.getLogger(__name__)

class UnsplashClient:
    def __init__(self):
        self.access_key = UNSPLASH_ACCESS_KEY
        self.base_url = "https://api.unsplash.com"

    def _translate_text(self, text):
        """Переводит английский текст на русский через GigaChat"""
        if not text:
            return ""
        try:
            from bot.gigachat import GigaChatClient
            giga = GigaChatClient()
            prompt = f"Переведи на русский язык (только перевод, без кавычек и пояснений): {text}"
            return giga.generate_short_sentence(prompt)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    def search_photo(self, query, orientation="landscape", per_page=5):
        """Возвращает (url, description) или (None, None)"""
        if not self.access_key:
            return None, None

        url = f"{self.base_url}/search/photos"
        headers = {"Authorization": f"Client-ID {self.access_key}"}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": orientation,
            "page": random.randint(1, 10)
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["results"]:
                    idx = random.randint(0, len(data["results"]) - 1)
                    photo = data["results"][idx]
                    description = photo.get("alt_description") or photo.get("description") or ""
                    if description:
                        words = description.split()
                        if len(words) > 15:
                            description = " ".join(words[:15])
                        description = self._translate_text(description)
                    return photo["urls"]["regular"], description
        except Exception as e:
            logger.error(f"Unsplash search error: {e}")

        return None, None

    def download_photo(self, url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            logger.error(f"Unsplash download error: {e}")
        return None