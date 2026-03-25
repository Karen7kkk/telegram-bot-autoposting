import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from aiogram.types import InputFile
from bot.gigachat import GigaChatClient
from bot.unsplash import UnsplashClient

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self, bot: Bot, channel_id: int, topic: str, interval_hours: int):
        self.bot = bot
        self.channel_id = channel_id
        self.topic = topic
        self.interval = interval_hours * 3600
        self.giga = GigaChatClient()
        self.unsplash = UnsplashClient()
        self.running = False
        self.task = None

    async def generate_and_post(self):
        try:
            # 1. Находим фото
            photo_url = self.unsplash.search_photo(self.topic)
            photo_bytes = self.unsplash.download_photo(photo_url)

            # 2. Пытаемся получить описание от Gemini
            from bot.gemini import describe_photo
            caption = describe_photo(photo_bytes)

            # 3. Если Gemini не сработал, падаем на короткое предложение по теме
            if not caption:
                caption = self.giga.generate_short_sentence(self.topic)

            # 4. Отправляем в канал
            await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=InputFile(photo_bytes),
                caption=f"📸 *{caption}*",
                parse_mode="Markdown"
            )
            logger.info(f"Photo post published at {datetime.now()}")
        except Exception as e:
            logger.error(f"Failed to post: {e}")

    async def run(self):
        self.running = True
        while self.running:
            await self.generate_and_post()
            await asyncio.sleep(self.interval)

    def start(self):
        if not self.running:
            self.task = asyncio.create_task(self.run())

    def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()