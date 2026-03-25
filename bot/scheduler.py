import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from aiogram.types import BufferedInputFile
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
            photo_url, description = self.unsplash.search_photo(self.topic)

            if not photo_url:
                caption = self.giga.generate_short_sentence(self.topic)
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=f"✨ {caption}",
                    parse_mode="Markdown"
                )
                logger.info(f"Text post published at {datetime.now()}")
                return

            photo_bytes = self.unsplash.download_photo(photo_url)
            if not photo_bytes:
                caption = self.giga.generate_short_sentence(self.topic)
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=f"✨ {caption}",
                    parse_mode="Markdown"
                )
                return

            if description:
                caption = description
            else:
                caption = self.giga.generate_short_sentence(self.topic)

            await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=BufferedInputFile(photo_bytes, filename="photo.jpg"),
                caption=f"📸 {caption}",
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