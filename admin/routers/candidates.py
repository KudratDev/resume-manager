import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from admin.core.database import db_cursor
from admin.core.security import get_current_user

router = APIRouter()
VALID_STATUSES = {"new", "reviewing", "interview", "hired", "rejected"}


class StatusUpdate(BaseModel):
    status: str


def _parse_languages(raw) -> dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return {}
    return {}


def _enrich(row: dict) -> dict:
    """Добавляет текущий статус к строке кандидата."""
    d = dict(row)
    d["languages"] = _parse_languages(d.get("languages"))
    return d


@router.get("")
def list_candidates(
        search: Optional[str] = Query(None, description="Поиск по имени или телефону"),
        status: Optional[str] = Query(None, description="Фильтр по статусу"),
        vacancy: Optional[str] = Query(None, description="Фильтр по вакансии"),
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
):
    """
    Список кандидатов с поиском и фильтрами.
    Статус берётся из последней заметки кандидата.
    """
    filters = []
    params = []

    if search:
        filters.append("(r.name ILIKE %s OR r.phone ILIKE %s)")
        like = f"%{search}%"
        params += [like, like]

    if vacancy:
        filters.append("r.vacancy ILIKE %s")
        params.append(f"%{vacancy}%")

    where_resume = ("WHERE " + " AND ".join(filters)) if filters else ""

    # Подзапрос для последнего статуса
    status_subq = """
        LEFT JOIN LATERAL (
            SELECT status FROM candidate_notes
            WHERE chat_id = r.chat_id
            ORDER BY created_at DESC
            LIMIT 1
        ) last_note ON TRUE
    """

    status_filter = ""
    if status:
        status_filter = "AND COALESCE(last_note.status, 'new') = %s"
        params.append(status)

    query = f"""
        SELECT
            r.chat_id,
            r.name,
            r.phone,
            r.vacancy,
            r.birthdate,
            r.education,
            r.experience,
            r.salary_expectation,
            r.cv_file_id,
            r.updated_at,
            COALESCE(last_note.status, 'new') AS status
        FROM resume_blanc r
        {status_subq}
        {where_resume}
        {status_filter}
        ORDER BY r.updated_at DESC
        LIMIT %s OFFSET %s
    """
    params += [limit, offset]

    with db_cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

        # Общий счётчик
        count_query = f"""
            SELECT COUNT(*) as total
            FROM resume_blanc r
            {status_subq}
            {where_resume}
            {status_filter}
        """
        cur.execute(count_query, params[:-2])  # без limit/offset
        total = cur.fetchone()["total"]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [dict(r) for r in rows],
    }


@router.get("/{chat_id}")
def get_candidate(chat_id: int):
    """Полная анкета кандидата."""
    with db_cursor() as cur:
        cur.execute("SELECT * FROM resume_blanc WHERE chat_id = %s", (chat_id,))
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Кандидат не найден")

    return _enrich(dict(row))


@router.patch("/{chat_id}/status")
def update_status(
        chat_id: int,
        body: StatusUpdate,
        current_user: dict = Depends(get_current_user),
):
    """Смена статуса кандидата. Создаёт запись в candidate_notes."""
    if body.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Допустимые статусы: {', '.join(VALID_STATUSES)}",
        )

    with db_cursor() as cur:
        cur.execute("SELECT chat_id FROM resume_blanc WHERE chat_id = %s", (chat_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Кандидат не найден")

        cur.execute(
            """
            INSERT INTO candidate_notes (chat_id, hr_id, status)
            VALUES (%s, %s, %s)
            """,
            (chat_id, current_user["id"], body.status),
        )

    return {"chat_id": chat_id, "status": body.status}
