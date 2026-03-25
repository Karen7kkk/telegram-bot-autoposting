from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from bot.scheduler import PostScheduler
from bot.gigachat import GigaChatClient
from bot.unsplash import UnsplashClient
from aiogram.types import InputFile
from bot.gemini import describe_photo

router = Router()
scheduler = None

@router.message()
async def handle_message(message: Message):
    global scheduler
    text = message.text or ""
    if text.startswith("/start_autopost"):
        args = text.split()
        if len(args) < 4:
            await message.answer("Usage: /start_autopost CHANNEL_ID TOPIC INTERVAL_HOURS")
            return
        try:
            channel_id = int(args[1])
            topic = args[2]
            interval = int(args[3])
            scheduler = PostScheduler(message.bot, channel_id, topic, interval)
            scheduler.start()
            await message.answer(f"✅ Autoposting started!\nChannel: {channel_id}\nTopic: {topic}\nInterval: {interval} hours")
        except Exception as e:
            await message.answer(f"❌ Error: {e}")

    elif text.startswith("/test_photo"):
        topic = text.replace("/test_photo", "").strip()
        if not topic:
            await message.answer("Укажи тему: /test_photo природа")
            return
        await message.answer("🔍 Генерирую фото и подпись...")
        try:
            unsplash = UnsplashClient()
            giga = GigaChatClient()

            photo_url = unsplash.search_photo(topic)
            if not photo_url:
                caption = giga.generate_short_sentence(topic)
                await message.answer(f"📝 *{caption}*", parse_mode="Markdown")
                return

            photo_bytes = unsplash.download_photo(photo_url)
            if not photo_bytes:
                caption = giga.generate_short_sentence(topic)
                await message.answer(f"📝 *{caption}*", parse_mode="Markdown")
                return

            caption = describe_photo(photo_bytes)
            if not caption:
                caption = giga.generate_short_sentence(topic)

            await message.answer_photo(
                photo=BufferedInputFile(photo_bytes, filename="photo.jpg"),
                caption=caption
            )
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
    else:
        await message.answer(f"Получено: {text}")
