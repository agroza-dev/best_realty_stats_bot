from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from common import config


def get_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton('За сегодня', callback_data=f'{config.Keyboard.CURRENT_DAY_ACTIVITY}'),
            InlineKeyboardButton('За вчера', callback_data=f'{config.Keyboard.LAST_DAY_ACTIVITY}')
        ],
        [
            InlineKeyboardButton('За 3 дня', callback_data=f'{config.Keyboard.LAST_THREE_DAYS_ACTIVITY}'),
            InlineKeyboardButton('За неделю', callback_data=f'{config.Keyboard.LAST_WEEK_ACTIVITY}'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
