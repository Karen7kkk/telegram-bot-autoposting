import google.generativeai as genai
from bot.config import GEMINI_API_KEY

# Инициализация Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

def describe_photo(photo_bytes: bytes) -> str:
    """
    Описывает фото коротким предложением (до 10 слов).
    Возвращает строку или пустую строку при ошибке.
    """
    if not model:
        return ""

    try:
        prompt = "Напиши одно короткое предложение (до 10 слов), описывающее это изображение."
        response = model.generate_content([prompt, photo_bytes])
        text = response.text.strip()
        if len(text.split()) > 10:
            text = " ".join(text.split()[:10])
        return text
    except Exception as e:
        print(f"Gemini error: {e}")
        return ""