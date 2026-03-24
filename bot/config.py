import os 
from dotenv import load_dotenv 
from pathlib import Path 
 
env_path = Path(__file__).parent.parent / ".env" 
load_dotenv(env_path) 
 
BOT_TOKEN = os.getenv("BOT_TOKEN") 
GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY") 
 
if not BOT_TOKEN: 
    raise ValueError("BOT_TOKEN not found") 
if not GIGACHAT_API_KEY: 
    raise ValueError("GIGACHAT_API_KEY not found") 
