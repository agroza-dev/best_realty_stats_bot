from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, Application

from common import logger
from common.config import config
from common.models.customer_activity import get_raw_activity, group_activity_by_status, get_plot
from services.bot_service.handlers.keyboards import get_keyboard
from services.bot_service.handlers.response import send_photo, send_response
from services.bot_service.templates import render_template


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = datetime.now(config.Date.TIMEZONE)
    d_start = (date - timedelta(days=0)).date()
    activity = await get_raw_activity(date_start=d_start, date_end=None)
    activity = await group_activity_by_status(activity)

    params = {
        'range': {
            'start': d_start.strftime("%d %B"),
            'end': None
        },
        'activity': activity,
    }

    if not activity:
        return None

    image_path = await get_plot(activity, d_start.strftime("%d %B"))

    await send_photo(
        update,
        context,
        photo=image_path,
        text=render_template("default_stats.j2", params),
        keyboard=get_keyboard(),
        update_message=True
    )


async def daily_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    await handler(context.update, context)


def set_daily_message(application: Application, chat_id: int, time_: datetime.time) -> None:
    now = datetime.now()
    time_with_tz = config.Date.TIMEZONE.localize(datetime.combine(now.date(), time_))
    application.job_queue.run_daily(
        daily_message,
        time=time_with_tz.timetz(),
        data=chat_id,
        name=str(chat_id),
    )