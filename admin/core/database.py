import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


def _get_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def get_connection():
    return psycopg2.connect(_get_url(), cursor_factory=RealDictCursor)


@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """
    Создаёт таблицы для admin-панели.
    Таблица resume_blanc уже существует (создаётся ботом).
    """
    with db_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS hr_users (
                id          SERIAL PRIMARY KEY,
                email       TEXT UNIQUE NOT NULL,
                password    TEXT NOT NULL,
                name        TEXT NOT NULL DEFAULT '',
                is_active   BOOLEAN NOT NULL DEFAULT TRUE,
                created_at  TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS candidate_notes (
                id          SERIAL PRIMARY KEY,
                chat_id     BIGINT NOT NULL,
                hr_id       INT REFERENCES hr_users(id) ON DELETE SET NULL,
                status      TEXT NOT NULL DEFAULT 'new',
                note        TEXT,
                created_at  TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_notes_chat_id
            ON candidate_notes(chat_id)
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id          SERIAL PRIMARY KEY,
                title       TEXT NOT NULL,
                description TEXT,
                is_active   BOOLEAN NOT NULL DEFAULT TRUE,
                created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

        cur.execute("SELECT COUNT(*) as cnt FROM vacancies")
        if cur.fetchone()["cnt"] == 0:
            cur.execute("""
                INSERT INTO vacancies (title, description) VALUES
                ('Business Analyst', 'Анализ бизнес-процессов, документация, работа с командой разработки.'),
                ('GIS Analyst', 'Работа с GIS системами, создание карт, интеграция геоданных.')
            """)
