import random
import requests
from bot.config import UNSPLASH_ACCESS_KEY

class UnsplashClient:
    def __init__(self):
        self.access_key = UNSPLASH_ACCESS_KEY
        self.base_url = "https://api.unsplash.com"

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
                    # Берём alt_description или description
                    description = photo.get("alt_description") or photo.get("description") or ""
                    # Ограничиваем длину
                    if len(description.split()) > 15:
                        description = " ".join(description.split()[:15])
                    return photo["urls"]["regular"], description
        except Exception:
            pass
        return None, None

    def download_photo(self, url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
        except Exception:
            pass
        return None