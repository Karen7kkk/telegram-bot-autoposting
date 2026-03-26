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

    if text.startswith("/start_autopost"):
        args = text.split()
        if len(args) < 4:
            await message.answer("Использование: /start_autopost ID_КАНАЛА ТЕМА ИНТЕРВАЛ_ЧАСОВ\nПример: /start_autopost -1001234567890 криптовалюта 3")
            return
        try:
            channel_id = int(args[1])
            topic = args[2]
            interval = int(args[3])
            scheduler = PostScheduler(message.bot, channel_id, topic, interval, use_pollinations=True)
            scheduler.start()
            await message.answer(f"✅ Автопостинг запущен!\nКанал: {channel_id}\nТема: {topic}\nИнтервал: {interval} часов\nГенерация: Pollinations.ai")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    elif text.startswith("/test_pollinations"):
        topic = text.replace("/test_pollinations", "").strip()
        if not topic:
            await message.answer("Укажи тему: /test_pollinations футбольный матч")
            return
        await message.answer("🎨 Генерирую изображение через Pollinations.ai... (10-20 секунд)")
        try:
            pollinations = PollinationsClient()
            giga = GigaChatClient()

            photo_bytes = pollinations.generate_image_russian(topic)

            if not photo_bytes:
                await message.answer("❌ Не удалось сгенерировать изображение. Попробуй другую тему.")
                return

            caption = giga.generate_short_sentence(topic)

            await message.answer_photo(
                photo=BufferedInputFile(photo_bytes, filename="generated.jpg"),
                caption=f"🎨 {caption}"
            )
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    elif text.startswith("/test_photo"):
        topic = text.replace("/test_photo", "").strip()
        if not topic:
            await message.answer("Укажи тему: /test_photo природа")
            return
        await message.answer("🔍 Ищу фото...")
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

            caption = description if description else giga.generate_short_sentence(topic)

            await message.answer_photo(
                photo=BufferedInputFile(photo_bytes, filename="photo.jpg"),
                caption=caption
            )
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    else:
        await message.answer(f"Получено: {text}")