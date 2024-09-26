from typing import cast

import telegram
from telegram import Chat, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import ContextTypes

from common import config


async def send_response(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    response: str,
    keyboard: InlineKeyboardMarkup | None = None,
) -> None:
    args = {
        "chat_id": _get_chat_id(update),
        "disable_web_page_preview": True,
        "text": response,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    if keyboard:
        args["reply_markup"] = keyboard

    await context.bot.send_message(**args)


async def send_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    photo: str,
    keyboard: InlineKeyboardMarkup | None = None,
    update_message: bool = False
) -> None:
    args = {
        "chat_id": _get_chat_id(update),
        "caption": text,
        "photo": photo,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    if keyboard:
        args["reply_markup"] = keyboard
    if update_message and hasattr(update, 'callback_query') and update.callback_query:
        if not keyboard:
            await update.callback_query.edit_message_media(
                media=InputMediaPhoto(
                    media=open(args['photo'], 'rb'),
                    caption=args['caption'],
                    parse_mode=args['parse_mode']
                )
            )
        else:
            await update.callback_query.edit_message_media(
                media=InputMediaPhoto(
                    media=open(args['photo'], 'rb'),
                    caption=args['caption'],
                    parse_mode=args['parse_mode']
                ),
                reply_markup=keyboard
            )
    else:
        await context.bot.send_photo(**args)


def _get_chat_id(update: Update) -> int:
    if not hasattr(update, 'effective_chat'):
        return config.Bot.TARGET_CHAT

    return cast(Chat, update.effective_chat).id
