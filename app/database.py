import os
import json
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
                vacancy             TEXT,
                name                TEXT,
                birthdate           TEXT,
                phone               TEXT,
                education           TEXT,
                gender              TEXT,
                marital_status      TEXT,
                languages           TEXT,
                salary_expectation  TEXT,
                disability          TEXT,
                vacancy_source      TEXT,
                experience          TEXT,
                certificates        TEXT,
                big_data_experience TEXT,
                memorable_project   TEXT,
                employment_format   TEXT,
                cv_file_id          TEXT,
                employment_type     TEXT,
                updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)


def save_or_update_resume(chat_id: int, data: dict) -> None:
    languages = data.get("languages")
    if isinstance(languages, dict):
        languages = json.dumps(languages, ensure_ascii=False)
    row = {
        "chat_id": chat_id,
        "vacancy": data.get("vacancy"),
        "name": data.get("name"),
        "birthdate": data.get("birthdate"),
        "phone": data.get("phone"),
        "education": data.get("education"),
        "gender": data.get("gender"),
        "marital_status": data.get("marital_status"),
        "languages": languages,
        "salary_expectation": data.get("salary_expectation"),
        "disability": data.get("disability"),
        "vacancy_source": data.get("vacancy_source"),
        "experience": data.get("experience"),
        "certificates": data.get("certificates"),
        "big_data_experience": data.get("big_data_experience"),
        "memorable_project": data.get("memorable_project"),
        "employment_format": data.get("employment_format"),
        "cv_file_id": data.get("cv_file_id"),
        "employment_type": data.get("employment_type"),
        "updated_at": datetime.now(),
    }
    with db_cursor() as cur:
        cur.execute("SELECT id FROM resume_blanc WHERE chat_id = %s", (chat_id,))
        exists = cur.fetchone()
        if exists:
            cur.execute("""
                UPDATE resume_blanc SET
                    vacancy             = %(vacancy)s,
                    name                = %(name)s,
                    birthdate           = %(birthdate)s,
                    phone               = %(phone)s,
                    education           = %(education)s,
                    gender              = %(gender)s,
                    marital_status      = %(marital_status)s,
                    languages           = %(languages)s,
                    salary_expectation  = %(salary_expectation)s,
                    disability          = %(disability)s,
                    vacancy_source      = %(vacancy_source)s,
                    experience          = %(experience)s,
                    certificates        = %(certificates)s,
                    big_data_experience = %(big_data_experience)s,
                    memorable_project   = %(memorable_project)s,
                    employment_format   = %(employment_format)s,
                    cv_file_id          = %(cv_file_id)s,
                    employment_type     = %(employment_type)s,
                    updated_at          = %(updated_at)s
                WHERE chat_id = %(chat_id)s
            """, row)
        else:
            cur.execute("""
                INSERT INTO resume_blanc
                    (chat_id, vacancy, name, birthdate, phone, education,
                     gender, marital_status, languages, salary_expectation,
                     disability, vacancy_source, experience, certificates,
                     big_data_experience, memorable_project, employment_format,
                     cv_file_id, employment_type, updated_at)
                VALUES
                    (%(chat_id)s, %(vacancy)s, %(name)s, %(birthdate)s, %(phone)s,
                     %(education)s, %(gender)s, %(marital_status)s, %(languages)s,
                     %(salary_expectation)s, %(disability)s, %(vacancy_source)s,
                     %(experience)s, %(certificates)s, %(big_data_experience)s,
                     %(memorable_project)s, %(employment_format)s, %(cv_file_id)s,
                     %(employment_type)s, %(updated_at)s)
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
