# database.py (добавьте эти методы к вашей существующей БД)
import sqlite3  # или asyncpg для PostgreSQL

# === Таблица пользователей (создать один раз) ===
"""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT,
    interest TEXT,
    subscribed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, interest),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    tags TEXT,  -- JSON или comma-separated: "text,image"
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

async def add_user_if_new(user_id: int, username: str = None, first_name: str = None):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
        (user_id, username, first_name)
    )
    cursor.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

async def add_user_interest(user_id: int, interest: str):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO user_interests (user_id, interest) VALUES (?, ?)",
        (user_id, interest)
    )
    conn.commit()
    conn.close()

async def subscribe_user_to_tag(user_id: int, interest: str):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user_interests SET subscribed = TRUE WHERE user_id = ? AND interest = ?",
        (user_id, interest)
    )
    conn.commit()
    conn.close()

async def get_top_posts_by_tag(interest: str, limit: int = 3):
    """Заглушка — замените на реальную логику выборки"""
    # Пример возврата
    return [
        {"id": 123, "title": f"Лучший инструмент для {interest}"},
        {"id": 124, "title": f"Как использовать {interest} в работе"},
        {"id": 125, "title": f"Сравнение сервисов: {interest}"},
    ]