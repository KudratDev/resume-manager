from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from admin.core.database import db_cursor
from admin.core.security import (
    verify_password, hash_password, create_token, get_current_user
)

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class CreateUserRequest(BaseModel):
    email: str
    password: str
    name: str = ""


@router.post("/login")
def login(body: LoginRequest):
    with db_cursor() as cur:
        cur.execute(
            "SELECT id, password, name, email FROM hr_users WHERE email = %s AND is_active = TRUE",
            (body.email,),
        )
        user = cur.fetchone()

    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    token = create_token(user["id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user["id"], "email": user["email"], "name": user["name"]},
    }


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/users", status_code=201)
def create_hr_user(body: CreateUserRequest, current_user: dict = Depends(get_current_user)):
    """Создать нового HR-пользователя. Только для авторизованных."""
    with db_cursor() as cur:
        cur.execute("SELECT id FROM hr_users WHERE email = %s", (body.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email уже занят")

        cur.execute(
            "INSERT INTO hr_users (email, password, name) VALUES (%s, %s, %s) RETURNING id",
            (body.email, hash_password(body.password), body.name),
        )
        new_id = cur.fetchone()["id"]

    return {"id": new_id, "email": body.email, "name": body.name}


@router.post("/bootstrap", status_code=201)
def bootstrap_admin(body: CreateUserRequest):
    """
    Создаёт первого HR-пользователя если таблица пустая.
    Вызвать один раз после деплоя, потом эндпоинт безопасен (вернёт 400).
    """
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM hr_users")
        if cur.fetchone()["cnt"] > 0:
            raise HTTPException(status_code=400, detail="Пользователи уже существуют")

        cur.execute(
            "INSERT INTO hr_users (email, password, name) VALUES (%s, %s, %s) RETURNING id",
            (body.email, hash_password(body.password), body.name),
        )
        new_id = cur.fetchone()["id"]

    return {"id": new_id, "email": body.email, "message": "Admin created"}
