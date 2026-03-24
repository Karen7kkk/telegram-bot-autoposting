from aiogram import Router
from aiogram.types import Message
from bot.scheduler import PostScheduler

router = Router()
scheduler = None

@router.message()
async def handle_message(message: Message):
    global scheduler
    if message.text and message.text.startswith("/start_autopost"):
        args = message.text.split()
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
    else:
        await message.answer(f"Got: {message.text}")