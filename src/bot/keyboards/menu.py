from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def generate_general_kb(date: datetime) -> InlineKeyboardMarkup:
    _keyboard = [
        [InlineKeyboardButton('🌌 Картинка дня', callback_data=f'pod:{date.strftime("%Y-%m-%d")}')],
        [InlineKeyboardButton('❤️ Избранное', callback_data='favorites:0')],
        [InlineKeyboardButton('🎲 Случайная картинка', callback_data='picture:random')],
    ]

    menu_markup = InlineKeyboardMarkup(_keyboard)
    return menu_markup

def generate_random_kb(date: datetime) -> InlineKeyboardMarkup:
    _kb = [
        [
            InlineKeyboardButton('🎲', callback_data='picture:random')
        ],
        [
            InlineKeyboardButton('❤️', callback_data=f'like:{date.strftime("%Y-%m-%d")}'),
            InlineKeyboardButton('🏠', callback_data='home')
        ]
    ]
    return InlineKeyboardMarkup(_kb)
