import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from app.config import BOT_TOKEN
from app.database import init_db
from app.handlers import handle_message, cmd_start

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Initialising database...")
    init_db()

    logger.info("Starting bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND,
        handle_message
    ))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
