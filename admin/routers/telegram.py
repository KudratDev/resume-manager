import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from admin.core.config import TELEGRAM_FILE_API, TELEGRAM_FILE_CDN, BOT_TOKEN
from admin.core.database import db_cursor

router = APIRouter()


class NotifyRequest(BaseModel):
    chat_id: int
    message: str


@router.post("/notify")
async def notify_candidate(
        body: NotifyRequest,
):
    """Отправить Telegram-сообщение кандидату."""
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="BOT_TOKEN не настроен")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{TELEGRAM_FILE_API}/sendMessage",
            json={"chat_id": body.chat_id, "text": body.message},
            timeout=10,
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Telegram API вернул ошибку")

    return {"ok": True, "chat_id": body.chat_id}


@router.get("/cv/{chat_id}")
async def get_cv(chat_id: int):
    """
    Проксирует CV-файл из Telegram.
    Frontend делает GET /telegram/cv/{chat_id} с JWT — получает файл напрямую.
    """
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="BOT_TOKEN не настроен")

    with db_cursor() as cur:
        cur.execute(
            "SELECT cv_file_id FROM resume_blanc WHERE chat_id = %s", (chat_id,)
        )
        row = cur.fetchone()

    if not row or not row["cv_file_id"]:
        raise HTTPException(status_code=404, detail="CV не найден")

    file_id = row["cv_file_id"]

    async with httpx.AsyncClient() as client:
        # Шаг 1: получить file_path от Telegram
        info = await client.get(
            f"{TELEGRAM_FILE_API}/getFile",
            params={"file_id": file_id},
            timeout=10,
        )
        data = info.json()
        if not data.get("ok"):
            raise HTTPException(status_code=502, detail="Не удалось получить файл от Telegram")

        file_path = data["result"]["file_path"]

        # Шаг 2: скачать и проксировать
        download_url = f"{TELEGRAM_FILE_CDN}/{file_path}"
        file_resp = await client.get(download_url, timeout=30)

    # Определяем Content-Type по расширению
    content_type = "application/octet-stream"
    if file_path.endswith(".pdf"):
        content_type = "application/pdf"
    elif file_path.endswith(".docx"):
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif file_path.endswith(".doc"):
        content_type = "application/msword"

    filename = file_path.split("/")[-1]

    return StreamingResponse(
        iter([file_resp.content]),
        media_type=content_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
