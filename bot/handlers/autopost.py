from aiogram import Router 
from aiogram.filters import Command 
from aiogram.types import Message 
 
router = Router() 
 
@router.message(Command("start_autopost")) 
async def start_autopost(message: Message): 
    await message.answer("TEST: Command received!") 
    args = message.text.split() 
    await message.answer(f"Args: {args}") 
