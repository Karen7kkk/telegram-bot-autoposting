import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env")
if not GIGACHAT_API_KEY:
    raise ValueError("GIGACHAT_API_KEY not found in .env")
# Unsplash и Gemini могут отсутствовать – только предупреждения
if not UNSPLASH_ACCESS_KEY:
    print("Warning: UNSPLASH_ACCESS_KEY not set. Images may not work.")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not set. Captions will fallback to topic-based.")