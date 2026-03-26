import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from aiogram.types import BufferedInputFile
from bot.gigachat import GigaChatClient
from bot.unsplash import UnsplashClient
from bot.pollinations import PollinationsClient
from bot.config import POLLINATIONS_API_KEY

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self, bot: Bot, channel_id: int, topic: str, interval_hours: int, use_pollinations: bool = True):
        self.bot = bot
        self.channel_id = channel_id
        self.topic = topic
        self.interval = interval_hours * 3600
        self.giga = GigaChatClient()
        self.use_pollinations = use_pollinations
        self.unsplash = UnsplashClient()
        # Инициализируем Pollinations только если есть ключ
        self.pollinations = PollinationsClient() if use_pollinations and POLLINATIONS_API_KEY else None
        self.running = False
        self.task = None

    async def generate_and_post(self):
        """
        Основной метод генерации и публикации поста
        Сначала пытается сгенерировать изображение через Pollinations,
        если не получается — использует Unsplash,
        если и Unsplash не работает — отправляет только текст
        """
        try:
            photo_bytes = None
            caption = None

            # 1. Пробуем Pollinations.ai (генерация уникальных изображений)
            if self.use_pollinations and self.pollinations:
                logger.info(f"Generating image via Pollinations for topic: {self.topic}")
                photo_bytes = self.pollinations.generate_image_russian(self.topic)

                if photo_bytes:
                    caption = self.giga.generate_short_sentence(self.topic)
                    logger.info(f"Image generated via Pollinations, size: {len(photo_bytes)} bytes")
                else:
                    logger.warning("Pollinations failed, falling back to Unsplash")

            # 2. Если Pollinations не сработал, используем Unsplash
            if not photo_bytes:
                logger.info(f"Searching photo via Unsplash for topic: {self.topic}")
                photo_url, description = self.unsplash.search_photo(self.topic)

                if photo_url:
                    photo_bytes = self.unsplash.download_photo(photo_url)
                    if photo_bytes:
                        caption = description if description else self.giga.generate_short_sentence(self.topic)
                        logger.info(f"Photo found via Unsplash, size: {len(photo_bytes)} bytes")
                    else:
                        logger.warning("Failed to download photo from Unsplash")
                else:
                    logger.warning("No photo found on Unsplash")

            # 3. Если есть фото — отправляем с подписью
            if photo_bytes:
                # Выбираем эмодзи в зависимости от источника
                if self.use_pollinations and self.pollinations:
                    emoji = "🎨"
                else:
                    emoji = "📸"

                await self.bot.send_photo(
                    chat_id=self.channel_id,
                    photo=BufferedInputFile(photo_bytes, filename="post.jpg"),
                    caption=f"{emoji} *{caption}*" if caption else f"{emoji} {self.topic}",
                    parse_mode="Markdown"
                )
                logger.info(f"Post published at {datetime.now()}")

            # 4. Если нет фото — отправляем только текст
            else:
                caption = self.giga.generate_short_sentence(self.topic)
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=f"✨ *{caption}*",
                    parse_mode="Markdown"
                )
                logger.info(f"Text-only post published at {datetime.now()}")

        except Exception as e:
            logger.error(f"Failed to post: {e}")

    async def run(self):
        """
        Основной цикл планировщика
        """
        self.running = True
        logger.info(f"Scheduler started for channel {self.channel_id}, topic: {self.topic}, interval: {self.interval // 3600} hours")

        while self.running:
            await self.generate_and_post()
            logger.info(f"Waiting {self.interval // 3600} hours until next post...")
            await asyncio.sleep(self.interval)

    def start(self):
        """
        Запускает планировщик
        """
        if not self.running:
            self.task = asyncio.create_task(self.run())
            logger.info(f"Scheduler started for topic: {self.topic}")

    def stop(self):
        """
        Останавливает планировщик
        """
        self.running = False
        if self.task:
            self.task.cancel()
            logger.info(f"Scheduler stopped for topic: {self.topic}")