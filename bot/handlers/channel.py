from aiogram import Router 
from aiogram.filters import Command 
from aiogram.types import Message 
 
router = Router() 
 
last_forwarded_id = None 
 
@router.message() 
async def catch_forward(message: Message): 
    global last_forwarded_id 
    if message.forward_from_chat: 
        last_forwarded_id = message.forward_from_chat.id 
        await message.answer(f"Channel detected! ID: {last_forwarded_id}\nNow send /channel_id to confirm") 
 
@router.message(Command("channel_id")) 
async def get_channel_id(message: Message): 
    global last_forwarded_id 
    if last_forwarded_id: 
        await message.answer(f"? Channel ID: {last_forwarded_id}") 
    else: 
        await message.answer("Please forward a message from your channel first, then send /channel_id") 
