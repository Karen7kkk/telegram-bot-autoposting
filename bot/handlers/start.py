# handlers/start.py
from aiogram import Router, F, types
from aiogram.filters import Command
from database import db  # ваш модуль БД
from keyboards.interests import get_interests_keyboard, get_after_interest_keyboard

router = Router()

# === Сценарий 1: /start ===
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # Сохраняем пользователя, если новый
    await db.add_user_if_new(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    await message.answer(
        "👋 Привет! Я — ваш гид по миру нейросетей.\n\n"
        "Помогу быстро найти:\n"
        "• Инструменты для текста, картинок и видео\n"
        "• Готовые промпты и инструкции\n"
        "• Бесплатные и локальные решения\n\n"
        "Выберите, что вам интересно прямо сейчас 👇",
        reply_markup=get_interests_keyboard()
    )

# === Сценарий 2: выбор интереса ===
@router.callback_query(F.data.startswith("interest:"))
async def process_interest(callback: types.CallbackQuery):
    interest = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    # 1. Сохраняем интерес в БД
    await db.add_user_interest(user_id, interest)
    
    # 2. Получаем топ-3 поста по тегу (заглушка — замените на реальную выборку)
    posts = await db.get_top_posts_by_tag(interest, limit=3)
    
    # 3. Формируем текст ответа
    if posts:
        post_links = "\n".join([f"{i+1}️⃣ «{p['title']}»\n   🔗 /post_{p['id']}" for i, p in enumerate(posts)])
        text = (
            f"✅ Отлично, работаем с «{interest}»!\n\n"
            f"Вот 3 лучших материала по теме:\n\n"
            f"{post_links}\n\n"
            f"💡 Хотите получать только подборки по этой теме?"
        )
    else:
        text = (
            f"✅ Вы выбрали «{interest}»!\n\n"
            f"Пока здесь нет постов, но я уже готовлю подборку 🔜\n"
            f"А пока посмотрите другие категории или подпишитесь на обновления."
        )
    
    # 4. Отправляем ответ с кнопками
    await callback.message.edit_text(
        text,
        reply_markup=get_after_interest_keyboard(interest)
    )
    await callback.answer()

# === Сценарий 3: подписка на рубрику ===
@router.callback_query(F.data.startswith("sub:"))
async def process_subscription(callback: types.CallbackQuery):
    interest = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    await db.subscribe_user_to_tag(user_id, interest)
    
    await callback.message.edit_text(
        f"✅ Вы подписаны на рубрику «{interest}»!\n\n"
        f"Теперь вы будете получать:\n"
        f"• Новые инструменты по этой теме\n"
        f"• Разборы промптов и кейсы\n"
        f"• Сравнения моделей раз в 2–3 дня",
        reply_markup=get_after_interest_keyboard(interest)
    )
    await callback.answer("🔔 Подписка активирована!")