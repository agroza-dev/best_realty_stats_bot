from telegram import Update
from telegram.ext import ContextTypes

from services.bot_service.handlers.response import send_response
from services.bot_service.templates import render_template


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_response(update, context, response=render_template("start.j2"))
