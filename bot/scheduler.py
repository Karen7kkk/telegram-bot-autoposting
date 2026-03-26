import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from aiogram.types import BufferedInputFile
from bot.gigachat import GigaChatClient
from bot.unsplash import UnsplashClient

# Pollinations опционально
try:
    from bot.pollinations import PollinationsClient
    POLLINATIONS_AVAILABLE = True
except ImportError:
    POLLINATIONS_AVAILABLE = False
    PollinationsClient = None

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self, bot: Bot, channel_id: int, topic: str, interval_hours: int, use_pollinations: bool = False):
        self.bot = bot
        self.channel_id = channel_id
        self.topic = topic
        self.interval = interval_hours * 3600
        self.giga = GigaChatClient()
        self.use_pollinations = use_pollinations and POLLINATIONS_AVAILABLE
        self.unsplash = UnsplashClient()
        self.pollinations = PollinationsClient() if self.use_pollinations else None
        self.running = False
        self.task = None

    async def generate_and_post(self):
        try:
            photo_bytes = None
            caption = None

            # 1. Пробуем Pollinations если включен
            if self.use_pollinations and self.pollinations:
                logger.info(f"Generating via Pollinations: {self.topic}")
                photo_bytes = self.pollinations.generate_image_variations(self.topic)
                if photo_bytes:
                    caption = self.giga.generate_short_sentence(self.topic)

            # 2. Fallback на Unsplash
            if not photo_bytes:
                logger.info(f"Searching Unsplash: {self.topic}")
                photo_url, description = self.unsplash.search_photo(self.topic)
                if photo_url:
                    photo_bytes = self.unsplash.download_photo(photo_url)
                    if photo_bytes:
                        caption = description if description else self.giga.generate_short_sentence(self.topic)

            # 3. Отправка
            if photo_bytes:
                await self.bot.send_photo(
                    chat_id=self.channel_id,
                    photo=BufferedInputFile(photo_bytes, filename="post.jpg"),
                    caption=f"📸 *{caption}*" if not self.use_pollinations else f"🎨 *{caption}*",
                    parse_mode="Markdown"
                )
                logger.info(f"Post published at {datetime.now()}")
            else:
                caption = self.giga.generate_short_sentence(self.topic)
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=f"✨ *{caption}*",
                    parse_mode="Markdown"
                )
                logger.info(f"Text post published at {datetime.now()}")

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