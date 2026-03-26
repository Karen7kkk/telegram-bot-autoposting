import requests
import time
from bot.config import GIGACHAT_API_KEY

class GigaChatClient:
    def __init__(self):
        self.api_key = GIGACHAT_API_KEY
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
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