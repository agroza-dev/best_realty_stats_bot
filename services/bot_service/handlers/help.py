from telegram import Update
from telegram.ext import ContextTypes
from common.config import config
from services.bot_service.handlers.response import send_response
from services.bot_service.templates import render_template


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_response(
        update,
        context,
        response=render_template(
            "help.j2",
            {"manager": config.Contacts.MANAGER, "developer": config.Contacts.DEVELOPER}
        )
    )
