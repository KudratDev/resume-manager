from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from admin.core.database import db_cursor

router = APIRouter()


class VacancyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_active: bool = True


class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("")
def list_vacancies():
    with db_cursor() as cur:
        cur.execute("""
            SELECT v.*, COUNT(r.chat_id) AS candidate_count
            FROM vacancies v
            LEFT JOIN resume_blanc r ON r.vacancy = v.title
            GROUP BY v.id
            ORDER BY v.created_at DESC
        """)
        rows = cur.fetchall()
    return [dict(r) for r in rows]


@router.post("", status_code=201)
def create_vacancy(body: VacancyCreate):
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO vacancies (title, description, is_active) VALUES (%s, %s, %s) RETURNING *",
            (body.title, body.description, body.is_active),
        )
        row = cur.fetchone()
    return dict(row)


@router.patch("/{vacancy_id}")
def update_vacancy(
        vacancy_id: int,
        body: VacancyUpdate,
):
    fields, params = [], []
    if body.title is not None:
        fields.append("title = %s")
        params.append(body.title)
    if body.description is not None:
        fields.append("description = %s")
        params.append(body.description)
    if body.is_active is not None:
        fields.append("is_active = %s")
        params.append(body.is_active)

    if not fields:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")

    fields.append("updated_at = NOW()")
    params.append(vacancy_id)

    with db_cursor() as cur:
        cur.execute(
            f"UPDATE vacancies SET {', '.join(fields)} WHERE id = %s RETURNING *",
            params,
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Вакансия не найдена")

    return dict(row)


@router.delete("/{vacancy_id}", status_code=204)
def delete_vacancy(vacancy_id: int):
    with db_cursor() as cur:
        cur.execute("DELETE FROM vacancies WHERE id = %s RETURNING id", (vacancy_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Вакансия не найдена")
