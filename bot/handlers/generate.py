from aiogram import Router 
from aiogram.filters import Command 
from aiogram.types import Message 
from bot.gigachat import GigaChatClient 
 
router = Router() 
giga = GigaChatClient() 
 
@router.message(Command("generate")) 
async def cmd_generate(message: Message): 
    topic = message.text.replace("/generate", "").strip() 
    if not topic: 
        await message.answer("Please provide a topic. Example: /generate crypto") 
        return 
    await message.answer("?? Generating post... Please wait.") 
    try: 
        post = giga.generate_post(topic) 
        await message.answer(f"?? *Post about: {topic}*\n\n{post}", parse_mode="Markdown") 
    except Exception as e: 
        await message.answer(f"? Error: {e}") 
