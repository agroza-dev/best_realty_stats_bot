from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from common.config import config
from common.models.customer_activity import get_raw_activity, group_activity_by_status, get_plot
from services.bot_service.handlers.keyboards import get_keyboard
from services.bot_service.handlers.response import send_photo, send_response
from services.bot_service.templates import render_template


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = datetime.now(config.Date.TIMEZONE)
    d_start = (date - timedelta(days=7)).date()
    d_end = (date - timedelta(days=0)).date()

    activity = await get_raw_activity(date_start=d_start, date_end=d_end)
    activity = await group_activity_by_status(activity)

    d_start = d_start.strftime("%d %B")
    d_end = d_end.strftime("%d %B")

    params = {
        'range': {
            'start': d_start,
            'end': d_end,
        },
        'activity': activity,
    }

    if not activity:
        await send_response(
            update,
            context,
            render_template("default_stats.j2", params),
            keyboard=get_keyboard()
        )
        return None

    await send_response(
        update,
        context,
        render_template("default_stats.j2", params),
        keyboard=get_keyboard()
    )


