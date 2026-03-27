import asyncio
from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from bot.gigachat import GigaChatClient
from bot.unsplash import UnsplashClient
from bot.database import (
    add_rubric, get_rubrics, add_post,
    update_post_status, get_posts_by_status, get_post,
    get_rubric_by_name
)
from datetime import datetime

# Pollinations опционально
try:
    from bot.pollinations import PollinationsClient
    POLLINATIONS_AVAILABLE = True
except ImportError:
    POLLINATIONS_AVAILABLE = False
    PollinationsClient = None

router = Router()

@router.message()
async def handle_message(message: Message):
    text = message.text or ""

    # ============ КОМАНДА /newpost ============
    if text.startswith("/newpost"):
        parts = text.split(maxsplit=2)
        if len(parts) < 2:
            await message.answer("Использование: /newpost <тема> [рубрика]\nПример: /newpost криптовалюта технологии")
            return
        topic = parts[1]
        rubric_name = parts[2] if len(parts) > 2 else None
        rubric_id = None
        if rubric_name:
            rubric = get_rubric_by_name(rubric_name)
            if not rubric:
                await message.answer(f"Рубрика '{rubric_name}' не найдена. Сначала создайте её командой /add_rubric")
                return
            rubric_id = rubric["id"]
        post_id = add_post(topic=topic, rubric_id=rubric_id)
        await message.answer(f"✅ Пост #{post_id} создан со статусом 'draft'. Тема: {topic}\n"
                             f"Используйте /approve {post_id} для подтверждения или /schedule {post_id} <дата> для планирования.")

    # ============ КОМАНДА /drafts ============
    elif text.startswith("/drafts"):
        posts = get_posts_by_status("draft")
        if not posts:
            await message.answer("Нет черновиков.")
            return
        lines = [f"📝 {p['id']}: {p['topic']} (создан {p['created_at']})" for p in posts]
        await message.answer("\n".join(lines), parse_mode="Markdown")

    # ============ КОМАНДА /approve ============
    elif text.startswith("/approve"):
        parts = text.split()
        if len(parts) < 2:
            await message.answer("Использование: /approve <post_id>")
            return
        try:
            post_id = int(parts[1])
        except ValueError:
            await message.answer("ID поста должен быть числом.")
            return
        post = get_post(post_id)
        if not post:
            await message.answer(f"Пост #{post_id} не найден.")
            return
        if post["status"] != "draft":
            await message.answer(f"Пост #{post_id} не в статусе draft (текущий: {post['status']}).")
            return
        update_post_status(post_id, "approved")
        await message.answer(f"✅ Пост #{post_id} подтверждён. Теперь его можно запланировать: /schedule {post_id} <дата>")

    # ============ КОМАНДА /schedule ============
    elif text.startswith("/schedule"):
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            await message.answer("Использование: /schedule <post_id> <дата и время в формате YYYY-MM-DD HH:MM>\nПример: /schedule 42 2025-04-01 15:00")
            return
        try:
            post_id = int(parts[1])
        except ValueError:
            await message.answer("ID поста должен быть числом.")
            return
        date_str = parts[2]
        try:
            scheduled_at = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            await message.answer("Неверный формат даты. Используйте YYYY-MM-DD HH:MM")
            return
        post = get_post(post_id)
        if not post:
            await message.answer(f"Пост #{post_id} не найден.")
            return
        if post["status"] != "approved":
            await message.answer(f"Пост #{post_id} должен быть подтверждён (/approve) перед планированием.")
            return
        update_post_status(post_id, "scheduled", scheduled_at)
        await message.answer(f"✅ Пост #{post_id} запланирован на {scheduled_at}")

    # ============ КОМАНДА /rubrics ============
    elif text.startswith("/rubrics"):
        rubrics = get_rubrics()
        if not rubrics:
            await message.answer("Нет созданных рубрик. Добавьте командой /add_rubric <название>")
            return
        lines = [f"📂 {r['name']}: {r['description'] or 'без описания'}" for r in rubrics]
        await message.answer("\n".join(lines), parse_mode="Markdown")

    # ============ КОМАНДА /add_rubric (админ) ============
    elif text.startswith("/add_rubric"):
        # Замените на ваш Telegram ID (получить можно через @userinfobot)
        YOUR_ADMIN_ID = 123456789
        if message.from_user.id != YOUR_ADMIN_ID:
            await message.answer("❌ У вас нет прав на создание рубрик.")
            return
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Использование: /add_rubric <название> [описание]")
            return
        name = parts[1].strip()
        desc = ""
        if " " in name:
            name, desc = name.split(maxsplit=1)
        add_rubric(name, desc)
        await message.answer(f"✅ Рубрика '{name}' создана.")

    # ============ КОМАНДА /scheduled (список запланированных) ============
    elif text.startswith("/scheduled"):
        posts = get_posts_by_status("scheduled")
        if not posts:
            await message.answer("Нет запланированных постов.")
            return
        lines = [f"⏰ {p['id']}: {p['topic']} (запланирован {p['scheduled_at']})" for p in posts]
        await message.answer("\n".join(lines), parse_mode="Markdown")

    # ============ КОМАНДА /test_photo (Unsplash) ============
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
            caption = description if description else giga.generate_short_sentence(topic)
            await message.answer_photo(
                photo=BufferedInputFile(photo_bytes, filename="photo.jpg"),
                caption=f"📸 {caption}"
            )
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    # ============ КОМАНДА /test_pollinations ============
    elif text.startswith("/test_pollinations") and POLLINATIONS_AVAILABLE:
        topic = text.replace("/test_pollinations", "").strip()
        if not topic:
            await message.answer("Укажи тему: /test_pollinations футбольный матч")
            return
        await message.answer("🎨 Генерирую изображение через Pollinations... (30-60 секунд)")
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
                    "❌ Не удалось сгенерировать изображение. Попробуй другую тему или используй /test_photo"
                )
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    # ============ КОМАНДА /test_variations ============
    elif text.startswith("/test_variations") and POLLINATIONS_AVAILABLE:
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
                await asyncio.sleep(2)
            await message.answer("✅ Генерация 3 вариантов завершена!")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    # ============ КОМАНДА /help ============
    elif text.startswith("/help"):
        help_text = """
📋 *Доступные команды бота:*

📝 *Управление постами:*
• `/newpost <тема> [рубрика]` — создать черновик
• `/drafts` — список черновиков
• `/approve <id>` — подтвердить пост
• `/schedule <id> <дата>` — запланировать публикацию (YYYY-MM-DD HH:MM)
• `/scheduled` — список запланированных

🏷️ *Рубрики:*
• `/rubrics` — список рубрик
• `/add_rubric <название>` — создать рубрику (админ)

🎨 *Генерация и поиск изображений:*
• `/test_photo <тема>` — найти фото в Unsplash
• `/test_pollinations <тема>` — сгенерировать изображение (если включён)
• `/test_variations <тема>` — 3 варианта

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