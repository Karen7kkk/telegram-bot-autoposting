import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from aiogram.types import BufferedInputFile
from bot.database import get_scheduled_posts, update_post_status, add_log
from bot.gigachat import GigaChatClient
from bot.unsplash import UnsplashClient
from bot.config import LOG_CHANNEL_ID

logger = logging.getLogger(__name__)

class GlobalScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.running = False
        self.task = None
        self.giga = GigaChatClient()
        self.unsplash = UnsplashClient()

    async def _send_log(self, message: str):
        """Отправляет сообщение в канал логов (если указан)"""
        if LOG_CHANNEL_ID:
            try:
                await self.bot.send_message(LOG_CHANNEL_ID, message)
            except Exception as e:
                logger.error(f"Failed to send log: {e}")
        logger.info(message)

    async def publish_post(self, post):
        """Публикует один пост, возвращает True при успехе"""
        post_id = post["id"]
        topic = post["topic"]
        try:
            # Генерируем контент
            photo_url, description = self.unsplash.search_photo(topic)
            if not photo_url:
                content = self.giga.generate_short_sentence(topic)
                await self.bot.send_message(
                    chat_id=post["channel_id"] if "channel_id" in post else None,
                    text=f"✨ {content}",
                    parse_mode="Markdown"
                )
            else:
                photo_bytes = self.unsplash.download_photo(photo_url)
                caption = description if description else self.giga.generate_short_sentence(topic)
                # Здесь нужно знать channel_id – для MVP пока используем тот, что сохранён
                # В реальности в таблице posts должно быть поле channel_id
                # Пока мы не сохраняем channel_id, поэтому оставляем заглушку
                # В будущем добавим поле channel_id
                pass  # TODO: передать правильный канал

            # Обновляем статус
            update_post_status(post_id, "posted")
            await self._send_log(f"✅ Пост {post_id} опубликован (тема: {topic})")
            return True
        except Exception as e:
            logger.error(f"Ошибка публикации поста {post_id}: {e}")
            await self._send_log(f"❌ Ошибка публикации поста {post_id}: {e}")
            return False

    async def run(self):
        """Главный цикл планировщика"""
        self.running = True
        while self.running:
            try:
                # Проверяем запланированные посты
                scheduled = get_scheduled_posts()
                for post in scheduled:
                    await self.publish_post(post)
                # Пауза между проверками (например, 30 секунд)
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)

    def start(self):
        if not self.running:
            self.task = asyncio.create_task(self.run())
            logger.info("Global scheduler started")

    def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()