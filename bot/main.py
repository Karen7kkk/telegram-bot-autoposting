# main.py (добавьте к существующему коду)
from aiogram import Bot, Dispatcher
from handlers import start, test  # импортируйте ваши роутеры
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    
    # Подключаем роутеры
    dp.include_router(start.router)  # ← новый роутер
    dp.include_router(test.router)   # ваш существующий
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())