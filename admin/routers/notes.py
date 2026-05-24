from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from admin.core.database import db_cursor
from admin.core.security import get_current_user

router = APIRouter()


class NoteCreate(BaseModel):
    note: str
    status: str = "new"


@router.get("/{chat_id}")
def get_notes(chat_id: int):
    """История заметок по кандидату (новые сначала)."""
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT
                cn.id,
                cn.chat_id,
                cn.status,
                cn.note,
                cn.created_at,
                hu.name AS hr_name,
                hu.email AS hr_email
            FROM candidate_notes cn
            LEFT JOIN hr_users hu ON hu.id = cn.hr_id
            WHERE cn.chat_id = %s
            ORDER BY cn.created_at DESC
            """,
            (chat_id,),
        )
        rows = cur.fetchall()

    return [dict(r) for r in rows]


@router.post("/{chat_id}", status_code=201)
def add_note(
        chat_id: int,
        body: NoteCreate,
        current_user: dict = Depends(get_current_user),
):
    """Добавить заметку (и опционально обновить статус)."""
    with db_cursor() as cur:
        cur.execute("SELECT chat_id FROM resume_blanc WHERE chat_id = %s", (chat_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Кандидат не найден")

        cur.execute(
            """
            INSERT INTO candidate_notes (chat_id, hr_id, status, note)
            VALUES (%s, %s, %s, %s)
            RETURNING id, created_at
            """,
            (chat_id, current_user["id"], body.status, body.note),
        )
        row = cur.fetchone()

    return {
        "id": row["id"],
        "chat_id": chat_id,
        "status": body.status,
        "note": body.note,
        "created_at": row["created_at"],
        "hr_name": current_user["name"],
    }
