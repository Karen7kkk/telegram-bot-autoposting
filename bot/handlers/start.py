from aiogram.filters import CommandStart
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    builder = InlineKeyboardBuilder()
    interests = [
        ("📝 Текст", "interest:text"),
        ("🎨 Картинки", "interest:image"),
        ("🎬 Видео", "interest:video"),
        ("💻 Код", "interest:code"),
        ("⚙️ Авто", "interest:automation"),
        ("🆓 Бесплатно", "interest:free"),
        ("🏠 Локально", "interest:local"),
        ("🎯 Все рубрики", "interest:all"),
    ]
    for text, cb in interests:
        builder.button(text=text, callback_data=cb)
    builder.adjust(2)  # 2 колонки
    
    await message.answer(
        "👋 Привет! Я — ваш гид по миру нейросетей...\nВыберите интерес 👇",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("interest:"))
async def process_interest(callback: CallbackQuery):
    interest = callback.data.split(":")[1]
    # 1. Сохраняем интерес в БД
    # 2. Получаем топ-3 поста по тегу
    # 3. Формируем ответ с кнопками дальнейших действий
    ...