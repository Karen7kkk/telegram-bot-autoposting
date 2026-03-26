import asyncio
from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from bot.scheduler import PostScheduler
from bot.gigachat import GigaChatClient
from bot.unsplash import UnsplashClient
from bot.pollinations import PollinationsClient

router = Router()
scheduler = None

@router.message()
async def handle_message(message: Message):
    global scheduler
    text = message.text or ""

    # ============ КОМАНДА /start_autopost ============
    if text.startswith("/start_autopost"):
        args = text.split()
        if len(args) < 4:
            await message.answer(
                "Использование: /start_autopost ID_КАНАЛА ТЕМА ИНТЕРВАЛ_ЧАСОВ\n"
                "Пример: /start_autopost -1001234567890 криптовалюта 3"
            )
            return
        try:
            channel_id = int(args[1])
            topic = args[2]
            interval = int(args[3])
            scheduler = PostScheduler(
                message.bot, 
                channel_id, 
                topic, 
                interval, 
                use_pollinations=False  # Пока используем Unsplash как основной
            )
            scheduler.start()
            await message.answer(
                f"✅ Автопостинг запущен!\n"
                f"Канал: {channel_id}\n"
                f"Тема: {topic}\n"
                f"Интервал: {interval} часов\n"
                f"Источник: Unsplash (фото + русское описание)"
            )
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    # ============ КОМАНДА /test_gigachat_image ============
    elif text.startswith("/test_gigachat_image"):
        topic = text.replace("/test_gigachat_image", "").strip()
        if not topic:
            await message.answer("Укажи тему: /test_gigachat_image розовый кот в шляпе")
            return

        await message.answer("🎨 Генерирую изображение через GigaChat... (20-40 секунд)")

        try:
            giga = GigaChatClient()

            status_msg = await message.answer("⏳ Генерация изображения...")

            # Генерируем изображение
            photo_bytes = giga.generate_image_simple(topic)

            if photo_bytes:
                # Генерируем подпись
                caption = giga.generate_short_sentence(topic)
                await message.answer_photo(
                    photo=BufferedInputFile(photo_bytes, filename="generated.jpg"),
                    caption=f"🎨 GigaChat: {caption}"
                )
                await status_msg.delete()
            else:
                await status_msg.edit_text(
                    "❌ Не удалось сгенерировать изображение. "
                    "Попробуй другой промпт или используй /test_photo"
                )

        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    # ============ КОМАНДА /test_pollinations ============
    elif text.startswith("/test_pollinations"):
        topic = text.replace("/test_pollinations", "").strip()
        if not topic:
            await message.answer("Укажи тему: /test_pollinations футбольный матч")
            return

        await message.answer("🎨 Генерирую уникальное изображение через Pollinations... (30-60 секунд)")

        try:
            pollinations = PollinationsClient()
            giga = GigaChatClient()

            status_msg = await message.answer("⏳ Генерация...")

            photo_bytes = pollinations.generate_image_variations(topic)

            if not photo_bytes:
                await status_msg.edit_text("🔄 Пробую другой вариант...")
                photo_bytes = pollinations.generate_image_with_fallback(topic)

            if not photo_bytes:
                await status_msg.edit_text("🔄 Пробую простой запрос...")
                photo_bytes = pollinations.generate_image(topic)

            if photo_bytes:
                caption = giga.generate_short_sentence(topic)
                await message.answer_photo(
                    photo=BufferedInputFile(photo_bytes, filename="generated.jpg"),
                    caption=f"🎨 Pollinations: {caption}"
                )
                await status_msg.delete()
            else:
                await status_msg.edit_text(
                    "❌ Не удалось сгенерировать изображение. "
                    "Попробуй другую тему или используй /test_photo"
                )

        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    # ============ КОМАНДА /test_variations ============
    elif text.startswith("/test_variations"):
        topic = text.replace("/test_variations", "").strip()
        if not topic:
            await message.answer("Укажи тему: /test_variations природа")
            return

        await message.answer("🎨 Генерирую 3 разных варианта изображений через Pollinations...")

        try:
            pollinations = PollinationsClient()
            giga = GigaChatClient()

            for i in range(3):
                await message.answer(f"⏳ Генерирую вариант {i+1}/3...")
                photo_bytes = pollinations.generate_image_variations(topic)

                if photo_bytes:
                    caption = giga.generate_short_sentence(topic)
                    await message.answer_photo(
                        photo=BufferedInputFile(photo_bytes, filename=f"generated_{i}.jpg"),
                        caption=f"🎨 Вариант {i+1}: {caption}"
                    )
                else:
                    await message.answer(f"❌ Вариант {i+1} не удалось сгенерировать")

                await asyncio.sleep(2)  # Пауза между запросами

            await message.answer("✅ Генерация 3 вариантов завершена!")

        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    # ============ КОМАНДА /test_photo ============
    elif text.startswith("/test_photo"):
        topic = text.replace("/test_photo", "").strip()
        if not topic:
            await message.answer("Укажи тему: /test_photo природа")
            return

        await message.answer("🔍 Ищу фото в Unsplash...")

        try:
            unsplash = UnsplashClient()
            giga = GigaChatClient()

            photo_url, description = unsplash.search_photo(topic)

            if not photo_url:
                caption = giga.generate_short_sentence(topic)
                await message.answer(f"✨ {caption}", parse_mode="Markdown")
                return

            photo_bytes = unsplash.download_photo(photo_url)
            if not photo_bytes:
                caption = giga.generate_short_sentence(topic)
                await message.answer(f"✨ {caption}", parse_mode="Markdown")
                return

            # Используем описание от Unsplash (уже переведённое на русский)
            caption = description if description else giga.generate_short_sentence(topic)

            await message.answer_photo(
                photo=BufferedInputFile(photo_bytes, filename="photo.jpg"),
                caption=f"📸 {caption}"
            )

        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    # ============ КОМАНДА /help ============
    elif text.startswith("/help"):
        help_text = """
📋 *Доступные команды бота:*

🎨 *Генерация изображений:*
• `/test_gigachat_image тема` — генерация через GigaChat
• `/test_pollinations тема` — генерация через Pollinations
• `/test_variations тема` — 3 варианта через Pollinations
• `/test_photo тема` — поиск готового фото в Unsplash

🚀 *Автопостинг в канал:*
• `/start_autopost ID_КАНАЛА ТЕМА ИНТЕРВАЛ` — запуск автопостинга
   Пример: `/start_autopost -1001234567890 природа 3`

📖 *Справка:*
• `/help` — эта справка

*Примечание:* Все изображения сопровождаются подписями, сгенерированными GigaChat на русском языке.
        """
        await message.answer(help_text, parse_mode="Markdown")

    # ============ ЛЮБОЕ ДРУГОЕ СООБЩЕНИЕ ============
    else:
        await message.answer(
            f"Получено: {text}\n\n"
            f"Отправь /help для списка доступных команд."
        )