from telegram import Update
from common import logger
from common.config import config
from telegram.ext import CommandHandler, ApplicationBuilder, MessageHandler, filters
from services.bot_service.handlers import start as start_handler
from services.bot_service.handlers import help_handler


async def start() -> None:
    app = False
    try:
        app = ApplicationBuilder().token(config.Bot.TOKEN).build()

        app.add_handler(CommandHandler('start', start_handler))
        app.add_handler(CommandHandler('help', help_handler))

        await app.initialize()

        await app.start()
        logger.info("Bot started successfully.")

        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Polling started successfully.")

    except Exception:
        import traceback
        logger.error(traceback.format_exc())
