import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from datetime import datetime


def get_connection():
    url = os.getenv("DATABASE_URL", "")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, cursor_factory=RealDictCursor)


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
    with db_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resume_blanc (
                id                  SERIAL PRIMARY KEY,
                chat_id             BIGINT UNIQUE NOT NULL,
                name                TEXT,
                birthdate           TEXT,
                phone               TEXT,
                experience          TEXT,
                certificates        TEXT,
                big_data_experience TEXT,
                memorable_project   TEXT,
                preferred_job_type  TEXT,
                updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)


def save_or_update_resume(chat_id: int, data: dict) -> None:
    row = {
        "chat_id": chat_id,
        "name": data.get("name"),
        "birthdate": data.get("birthdate"),
        "phone": data.get("phone"),
        "experience": data.get("experience"),
        "certificates": data.get("certificates"),
        "big_data_experience": data.get("big_data_experience"),
        "memorable_project": data.get("memorable_project"),
        "preferred_job_type": data.get("preferred_job_type"),
        "updated_at": datetime.now(),
    }
    with db_cursor() as cur:
        cur.execute("SELECT id FROM resume_blanc WHERE chat_id = %s", (chat_id,))
        exists = cur.fetchone()
        if exists:
            cur.execute("""
                UPDATE resume_blanc SET
                    name                = %(name)s,
                    birthdate           = %(birthdate)s,
                    phone               = %(phone)s,
                    experience          = %(experience)s,
                    certificates        = %(certificates)s,
                    big_data_experience = %(big_data_experience)s,
                    memorable_project   = %(memorable_project)s,
                    preferred_job_type  = %(preferred_job_type)s,
                    updated_at          = %(updated_at)s
                WHERE chat_id = %(chat_id)s
            """, row)
        else:
            cur.execute("""
                INSERT INTO resume_blanc
                    (chat_id, name, birthdate, phone, experience,
                     certificates, big_data_experience, memorable_project,
                     preferred_job_type, updated_at)
                VALUES
                    (%(chat_id)s, %(name)s, %(birthdate)s, %(phone)s, %(experience)s,
                     %(certificates)s, %(big_data_experience)s, %(memorable_project)s,
                     %(preferred_job_type)s, %(updated_at)s)
            """, row)


def get_resume(chat_id: int) -> dict | None:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM resume_blanc WHERE chat_id = %s", (chat_id,))
        return cur.fetchone()


def is_blocked(chat_id: int) -> bool:
    """Возвращает True если с последнего обновления прошло менее 2 минут."""
    with db_cursor() as cur:
        cur.execute("""
            SELECT updated_at FROM resume_blanc WHERE chat_id = %s
        """, (chat_id,))
        row = cur.fetchone()
        if not row:
            return False
        delta = datetime.now() - row["updated_at"]
        return delta.total_seconds() < 120
