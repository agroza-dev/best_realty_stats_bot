import datetime

from telegram import Update
from telegram.ext import CommandHandler, ApplicationBuilder, CallbackQueryHandler

from common import logger
from common.config import config
from services.bot_service.handlers import get_current_day_stats, get_last_day_stats, get_last_three_days_stats, \
    get_last_week_stats, set_daily_message
from services.bot_service.handlers import help_handler
from services.bot_service.handlers import start_handler


async def start() -> None:
    try:
        app = ApplicationBuilder().token(config.Bot.TOKEN).build()

        app.add_handler(CommandHandler('start', start_handler))
        app.add_handler(CommandHandler('help', help_handler))
        app.add_handler(CommandHandler('getStats', get_current_day_stats))
        app.add_handler(CallbackQueryHandler(
            get_current_day_stats,
            pattern=f'^{config.Keyboard.CURRENT_DAY_ACTIVITY}')
        )
        app.add_handler(CallbackQueryHandler(
            get_last_day_stats,
            pattern=f'^{config.Keyboard.LAST_DAY_ACTIVITY}')
        )
        app.add_handler(CallbackQueryHandler(
            get_last_three_days_stats,
            pattern=f'^{config.Keyboard.LAST_THREE_DAYS_ACTIVITY}')
        )
        app.add_handler(CallbackQueryHandler(
            get_last_week_stats,
            pattern=f'^{config.Keyboard.LAST_WEEK_ACTIVITY}')
        )
        set_daily_message(
            app,
            config.Bot.TARGET_CHAT,
            time_=datetime.time(
                hour=config.Scheduler.SEND_DAILY_REPORT_AT['h'],
                minute=config.Scheduler.SEND_DAILY_REPORT_AT['m'],
                second=config.Scheduler.SEND_DAILY_REPORT_AT['s']
            )
        )
        await app.initialize()

        await app.start()
        logger.info("Bot started successfully.")

        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Polling started successfully.")

    except Exception:
        import traceback
        logger.error(traceback.format_exc())
