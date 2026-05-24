from fastapi import APIRouter
from admin.core.database import db_cursor

router = APIRouter()


@router.get("/summary")
def summary():
    """Основные метрики для дашборда."""
    with db_cursor() as cur:
        # Всего кандидатов
        cur.execute("SELECT COUNT(*) AS total FROM resume_blanc")
        total = cur.fetchone()["total"]

        # По статусам (последний статус каждого кандидата)
        cur.execute("""
            SELECT
                COALESCE(last_status.status, 'new') AS status,
                COUNT(*) AS cnt
            FROM resume_blanc r
            LEFT JOIN LATERAL (
                SELECT status FROM candidate_notes
                WHERE chat_id = r.chat_id
                ORDER BY created_at DESC
                LIMIT 1
            ) last_status ON TRUE
            GROUP BY COALESCE(last_status.status, 'new')
        """)
        by_status = {row["status"]: row["cnt"] for row in cur.fetchall()}

        # По вакансиям
        cur.execute("""
            SELECT vacancy, COUNT(*) AS cnt
            FROM resume_blanc
            WHERE vacancy IS NOT NULL
            GROUP BY vacancy
            ORDER BY cnt DESC
        """)
        by_vacancy = [{"vacancy": r["vacancy"], "count": r["cnt"]} for r in cur.fetchall()]

        # По источнику (откуда узнали о вакансии)
        cur.execute("""
            SELECT vacancy_source, COUNT(*) AS cnt
            FROM resume_blanc
            WHERE vacancy_source IS NOT NULL
            GROUP BY vacancy_source
            ORDER BY cnt DESC
            LIMIT 10
        """)
        by_source = [{"source": r["vacancy_source"], "count": r["cnt"]} for r in cur.fetchall()]

        # Новые за последние 7 дней
        cur.execute("""
            SELECT COUNT(*) AS cnt FROM resume_blanc
            WHERE updated_at >= NOW() - INTERVAL '7 days'
        """)
        last_7_days = cur.fetchone()["cnt"]

        # По полу
        cur.execute("""
            SELECT gender, COUNT(*) AS cnt
            FROM resume_blanc
            WHERE gender IS NOT NULL
            GROUP BY gender
        """)
        by_gender = {r["gender"]: r["cnt"] for r in cur.fetchall()}

    return {
        "total": total,
        "last_7_days": last_7_days,
        "by_status": by_status,
        "by_vacancy": by_vacancy,
        "by_source": by_source,
        "by_gender": by_gender,
    }
