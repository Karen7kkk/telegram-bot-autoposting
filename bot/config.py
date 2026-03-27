import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")
POLLINATIONS_ENABLED = os.getenv("POLLINATIONS_ENABLED", "false").lower() == "true"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found")
if not GIGACHAT_API_KEY:
    raise ValueError("GIGACHAT_API_KEY not found")
if not UNSPLASH_ACCESS_KEY:
    print("Warning: UNSPLASH_ACCESS_KEY not set. Unsplash images may not work.")