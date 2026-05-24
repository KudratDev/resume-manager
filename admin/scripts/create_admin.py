#!/usr/bin/env python3
"""
Запускай один раз после деплоя:
    python scripts/create_admin.py

Или через переменные окружения:
    ADMIN_EMAIL=hr@company.com ADMIN_PASSWORD=secret python scripts/create_admin.py
"""
import os
import sys

# чтобы работало из корня монорепо
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from admin.core.database import init_db, db_cursor
from admin.core.security import hash_password

email = os.getenv("ADMIN_EMAIL") or input("Email: ").strip()
password = os.getenv("ADMIN_PASSWORD") or input("Password: ").strip()
name = os.getenv("ADMIN_NAME", "HR Admin")

init_db()

with db_cursor() as cur:
    cur.execute("SELECT id FROM hr_users WHERE email = %s", (email,))
    if cur.fetchone():
        print(f"Пользователь {email} уже существует.")
        sys.exit(0)

    cur.execute(
        "INSERT INTO hr_users (email, password, name) VALUES (%s, %s, %s) RETURNING id",
        (email, hash_password(password), name),
    )
    new_id = cur.fetchone()["id"]

print(f"✅ Создан HR-пользователь: {email} (id={new_id})")
