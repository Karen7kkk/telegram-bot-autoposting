# keyboards/interests.py
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_interests_keyboard():
    """Клавиатура с интересами для /start"""
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
    
    for text, callback in interests:
        builder.button(text=text, callback_data=callback)
    
    builder.adjust(2)  # 2 колонки для мобильных
    return builder.as_markup()


def get_after_interest_keyboard(interest: str):
    """Кнопки после выбора интереса"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🔔 Подписаться на рубрику", callback_data=f"sub:{interest}")
    builder.button(text="📂 Все категории", callback_data="interest:all")
    builder.button(text="📬 Вернуться в канал", url="https://t.me/your_channel")  # ← замените на ваш канал
    
    builder.adjust(1)
    return builder.as_markup()