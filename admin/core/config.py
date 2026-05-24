import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "")
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# Telegram File API — для проксирования CV
TELEGRAM_FILE_API: str = f"https://api.telegram.org/bot{BOT_TOKEN}"
TELEGRAM_FILE_CDN: str = f"https://api.telegram.org/file/bot{BOT_TOKEN}"
