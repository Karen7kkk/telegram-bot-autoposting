import requests 
import json 
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
        headers = { 
            "Authorization": f"Bearer {self.api_key}", 
            "RqUID": "123e4567-e89b-12d3-a456-426614174000", 
            "Content-Type": "application/x-www-form-urlencoded" 
        } 
        data = {"scope": "GIGACHAT_API_PERS"} 
        response = requests.post(self.auth_url, headers=headers, data=data, verify=False) 
        if response.status_code == 200: 
            token_data = response.json() 
            self.access_token = token_data.get("access_token") 
            self.token_expires = time.time() + token_data.get("expires_at", 3600) 
            return self.access_token 
        else: 
            raise Exception(f"Auth error: {response.text}") 
 
    def _ensure_token(self): 
        if not self.access_token or time.time(): 
            self._get_token() 
        return self.access_token 
 
    def generate_post(self, topic): 
        self._ensure_token() 
        headers = { 
            "Authorization": f"Bearer {self.access_token}", 
            "Content-Type": "application/json" 
        } 
        prompt = f"Write a short Telegram post about: {topic}. Length: 300-500 chars. Use emojis. Friendly style." 
        data = { 
            "model": "GigaChat", 
            "messages": [ 
                {"role": "system", "content": "You are a copywriter creating engaging Telegram posts."}, 
                {"role": "user", "content": prompt} 
            ], 
            "temperature": 0.7, 
            "max_tokens": 500 
        } 
        response = requests.post(self.api_url, headers=headers, json=data, verify=False) 
        if response.status_code == 200: 
            result = response.json() 
            return result["choices"][0]["message"]["content"] 
        else: 
            return f"Error: {response.text}" 
