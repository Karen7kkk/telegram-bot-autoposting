import asyncio 
import logging 
from aiogram import Bot, Dispatcher 
from bot.config import BOT_TOKEN 
from bot.handlers.test import router as test_router 
 
async def main(): 
    logging.basicConfig(level=logging.INFO) 
    print("Bot is starting...") 
    bot = Bot(token=BOT_TOKEN) 
    dp = Dispatcher() 
    dp.include_router(test_router) 
    print("Bot is ready!") 
    await dp.start_polling(bot) 
 
if __name__ == "__main__": 
    asyncio.run(main()) 
