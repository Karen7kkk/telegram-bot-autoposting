import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from bot.database import get_scheduled_posts, update_post_status, add_log
from bot.gigachat import GigaChatClient
from bot.config import LOG_CHANNEL_ID

logger = logging.getLogger(__name__)

class GlobalScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.running = False
        self.task = None
        self.giga = GigaChatClient()

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
        channel_id = post.get("channel_id")

        if not channel_id:
            logger.error(f"Post {post_id} has no channel_id, skipping")
            await self._send_log(f"❌ Пост #{post_id} не имеет channel_id")
            return False

        try:
            # Генерируем короткое предложение
            caption = self.giga.generate_short_sentence(topic)

            # Отправляем в канал (только текст)
            await self.bot.send_message(
                chat_id=channel_id,
                text=f"✨ *{caption}*",
                parse_mode="Markdown"
            )

            # Обновляем статус
            update_post_status(post_id, "posted")
            await self._send_log(f"✅ Пост #{post_id} опубликован в канал {channel_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка публикации поста {post_id}: {e}")
            await self._send_log(f"❌ Ошибка публикации поста {post_id}: {e}")
            return False

    async def run(self):
        """Главный цикл планировщика"""
        self.running = True
        logger.info("Scheduler loop started")
        while self.running:
            try:
                # Проверяем запланированные посты
                logger.debug("Checking for scheduled posts...")
                scheduled = get_scheduled_posts()
                logger.debug(f"Found {len(scheduled)} scheduled posts")
                for post in scheduled:
                    await self.publish_post(post)
                # Пауза между проверками (30 секунд)
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