import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from bot.gigachat import GigaChatClient

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self, bot: Bot, channel_id: int, topic: str, interval_hours: int):
        self.bot = bot
        self.channel_id = channel_id
        self.topic = topic
        self.interval = interval_hours * 3600
        self.giga = GigaChatClient()
        self.running = False
        self.task = None

    async def generate_and_post(self):
        try:
            post = self.giga.generate_post(self.topic)
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=f"📝 *Пост на тему: {self.topic}*\n\n{post}",
                parse_mode="Markdown"
            )
            logger.info(f"Post published at {datetime.now()}")
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