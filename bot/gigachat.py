import requests
import time
import logging
from bot.config import GIGACHAT_API_KEY

logger = logging.getLogger(__name__)

class GigaChatClient:
    def __init__(self):
        self.api_key = GIGACHAT_API_KEY
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self.files_url = "https://gigachat.devices.sberbank.ru/api/v1/files"
        self.access_token = None
        self.token_expires = 0

    def _get_token(self):
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "RqUID": "123e4567-e89b-12d3-a456-426614174000",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"scope": "GIGACHAT_API_PERS"}
        response = requests.post(self.auth_url, headers=headers, data=data, verify=False)
        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.token_expires = time.time() + 3600
        return self.access_token

    def _ensure_token(self):
        if not self.access_token or time.time() >= self.token_expires:
            self._get_token()
        return self.access_token

    def generate_post(self, topic):
        self._ensure_token()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        prompt = f"Напиши короткий пост для Telegram канала на тему: {topic}. Используй эмодзи. Дружеский стиль. Объем: 300-500 символов."
        data = {
            "model": "GigaChat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }
        response = requests.post(self.api_url, headers=headers, json=data, verify=False)
        result = response.json()
        return result["choices"][0]["message"]["content"]

    def generate_short_sentence(self, topic):
        self._ensure_token()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        prompt = f"Напиши одно короткое предложение (до 10 слов) на тему: {topic}. Без эмодзи. Только предложение на русском языке."
        data = {
            "model": "GigaChat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 50
        }
        response = requests.post(self.api_url, headers=headers, json=data, verify=False)
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    def generate_image(self, prompt):
        """
        Генерирует изображение через GigaChat по текстовому запросу
        Возвращает bytes изображения или None
        """
        self._ensure_token()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "GigaChat",
            "messages": [
                {"role": "user", "content": f"Нарисуй изображение: {prompt}"}
            ],
            "function_call": "auto"
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data, verify=False, timeout=60)

            if response.status_code == 200:
                result = response.json()
                # Пробуем найти file_id
                file_id = self._extract_file_id(result)
                if file_id:
                    return self._download_image(file_id)
                else:
                    logger.error(f"Could not extract file_id from response")
                    return None
            else:
                logger.error(f"Image generation error: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            logger.error(f"Image generation exception: {e}")
            return None

    def _extract_file_id(self, response):
        """Извлекает file_id из ответа GigaChat"""
        try:
            if "choices" in response and response["choices"]:
                content = response["choices"][0]["message"]["content"]
                # Ищем file_id в тексте
                if "file_id" in content:
                    import json
                    import re
                    match = re.search(r'"file_id":\s*"([^"]+)"', content)
                    if match:
                        return match.group(1)
            if "attachments" in response:
                for att in response["attachments"]:
                    if "file_id" in att:
                        return att["file_id"]
            if "file_id" in response:
                return response["file_id"]
        except Exception as e:
            logger.error(f"Extract file_id error: {e}")
        return None

    def _download_image(self, file_id):
        """Скачивает изображение по file_id"""
        self._ensure_token()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        url = f"{self.files_url}/{file_id}/content"

        try:
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Download error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Download exception: {e}")
            return None

    def generate_image_simple(self, prompt):
        """Упрощённая версия генерации изображения"""
        return self.generate_image(prompt)