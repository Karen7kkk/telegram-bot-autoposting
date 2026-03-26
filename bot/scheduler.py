import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from aiogram.types import BufferedInputFile
from bot.gigachat import GigaChatClient
from bot.unsplash import UnsplashClient
from bot.pollinations import PollinationsClient

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
        self.pollinations = PollinationsClient() if use_pollinations else None
        self.running = False
        self.task = None

    async def generate_and_post(self):
        try:
            photo_bytes = None
            caption = None

            if self.use_pollinations and self.pollinations:
                # Генерация через Pollinations
                logger.info(f"Generating image via Pollinations for: {self.topic}")
                photo_bytes = self.pollinations.generate_image_russian(self.topic)

                if photo_bytes:
                    caption = self.giga.generate_short_sentence(self.topic)
                else:
                    logger.warning("Pollinations failed, falling back to Unsplash")
                    # Fallback на Unsplash
                    photo_url, description = self.unsplash.search_photo(self.topic)
                    if photo_url:
                        photo_bytes = self.unsplash.download_photo(photo_url)
                        caption = description if description else self.giga.generate_short_sentence(self.topic)
                    else:
                        caption = self.giga.generate_short_sentence(self.topic)
                        await self.bot.send_message(
                            chat_id=self.channel_id,
                            text=f"✨ {caption}",
                            parse_mode="Markdown"
                        )
                        return

            else:
                # Используем Unsplash
                photo_url, description = self.unsplash.search_photo(self.topic)
                if not photo_url:
                    caption = self.giga.generate_short_sentence(self.topic)
                    await self.bot.send_message(
                        chat_id=self.channel_id,
                        text=f"✨ {caption}",
                        parse_mode="Markdown"
                    )
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

                caption = description if description else self.giga.generate_short_sentence(self.topic)

            # Отправляем результат
            if photo_bytes:
                await self.bot.send_photo(
                    chat_id=self.channel_id,
                    photo=BufferedInputFile(photo_bytes, filename="post.jpg"),
                    caption=f"📸 *{caption}*" if not self.use_pollinations else f"🎨 *{caption}*",
                    parse_mode="Markdown"
                )
                logger.info(f"Post published at {datetime.now()}")
            else:
                logger.error("No image was generated/found")

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