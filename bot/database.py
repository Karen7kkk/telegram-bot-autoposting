import sqlite3
import logging
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data.db"
logger = logging.getLogger(__name__)

def get_connection():
    """Возвращает соединение с БД, включает поддержку внешних ключей"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Создаёт таблицы, если их нет"""
    with get_connection() as conn:
        # Таблица рубрик
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rubrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        """)
        # Таблица постов (добавлено поле channel_id)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content TEXT,
                media_url TEXT,
                status TEXT NOT NULL DEFAULT 'draft',
                rubric_id INTEGER,
                scheduled_at TIMESTAMP,
                posted_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                utm_tags TEXT,
                channel_id INTEGER,
                FOREIGN KEY (rubric_id) REFERENCES rubrics(id)
            )
        """)
        # Таблица логов
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                message TEXT,
                user_id INTEGER
            )
        """)
        conn.commit()
        logger.info("Database initialized")

# ========== CRUD для рубрик ==========
def add_rubric(name: str, description: str = "") -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO rubrics (name, description) VALUES (?, ?)",
            (name, description)
        )
        conn.commit()
        return cur.lastrowid

def get_rubrics():
    with get_connection() as conn:
        cur = conn.execute("SELECT id, name, description FROM rubrics ORDER BY name")
        return cur.fetchall()

def get_rubric_by_name(name: str):
    with get_connection() as conn:
        cur = conn.execute("SELECT id, name, description FROM rubrics WHERE name = ?", (name,))
        return cur.fetchone()

# ========== CRUD для постов ==========
def add_post(topic: str, content: str = "", media_url: str = "", rubric_id: int = None, utm_tags: str = "", channel_id: int = None) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO posts (topic, content, media_url, rubric_id, utm_tags, channel_id, status)
               VALUES (?, ?, ?, ?, ?, ?, 'draft')""",
            (topic, content, media_url, rubric_id, utm_tags, channel_id)
        )
        conn.commit()
        return cur.lastrowid

def update_post_content(post_id: int, content: str = None, media_url: str = None):
    updates = []
    params = []
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if media_url is not None:
        updates.append("media_url = ?")
        params.append(media_url)
    if not updates:
        return
    params.append(post_id)
    with get_connection() as conn:
        conn.execute(f"UPDATE posts SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()

def update_post_status(post_id: int, status: str, scheduled_at: datetime = None):
    with get_connection() as conn:
        if status == "scheduled" and scheduled_at:
            conn.execute(
                "UPDATE posts SET status = ?, scheduled_at = ? WHERE id = ?",
                (status, scheduled_at, post_id)
            )
        elif status == "posted":
            conn.execute(
                "UPDATE posts SET status = ?, posted_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, post_id)
            )
        else:
            conn.execute("UPDATE posts SET status = ? WHERE id = ?", (status, post_id))
        conn.commit()
        # Отладочный вывод
        cur = conn.execute("SELECT status FROM posts WHERE id = ?", (post_id,))
        row = cur.fetchone()
        logger.debug(f"post {post_id} new status = {row['status'] if row else None}")

def get_posts_by_status(status: str, limit: int = 50):
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM posts WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status, limit)
        )
        return cur.fetchall()

def get_post(post_id: int):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        return cur.fetchone()

def get_scheduled_posts():
    """Возвращает посты, запланированные на время <= сейчас и ещё не опубликованные"""
    now = datetime.now().isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM posts WHERE status = 'scheduled' AND scheduled_at <= ?",
            (now,)
        )
        return cur.fetchall()

def delete_post(post_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()

# ========== Логи ==========
def add_log(event_type: str, message: str, user_id: int = None):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO logs (event_type, message, user_id) VALUES (?, ?, ?)",
            (event_type, message, user_id)
        )
        conn.commit()