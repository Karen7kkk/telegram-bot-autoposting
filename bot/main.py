import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.handlers.test import router as test_router
from bot.database import init_db
from bot.scheduler import GlobalScheduler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    print("Bot is starting...")
    
    # Инициализация базы данных
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    bot = Bot(token=BOT_TOKEN)
    
    # Запуск глобального планировщика
    try:
        scheduler = GlobalScheduler(bot)
        scheduler.start()
        logger.info("Global scheduler started")
    except Exception as e:
        logger.error(f"Scheduler start failed: {e}")
    
    dp = Dispatcher()
    dp.include_router(test_router)
    
    print("Bot is ready!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())