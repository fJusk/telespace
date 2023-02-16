from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from typing import List
from datetime import datetime, timedelta


class PaginationKeyboard:

    def __init__(
        self, 
        prev_callback: str,
        next_callback: str,
        add: List[InlineKeyboardButton] = None
    ) -> None:

        keyboard = [
            [
                InlineKeyboardButton('<-', callback_data=prev_callback),
                InlineKeyboardButton('->', callback_data=next_callback),
            ],
            add
        ]
        self._keyboard = keyboard

    @property
    def keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(self._keyboard)


def generate_photo_pagination(
    current: datetime = datetime.now()
) -> PaginationKeyboard:
    prev_date = current + timedelta(days=1)
    next_date = current - timedelta(days=1)

    if prev_date > datetime.now():
        prev_date = datetime(year=2000, month=1, day=1)

    if next_date < datetime(year=2000, month=1, day=1):
        next_date = datetime.now()

    prev_callback = f"pod:{prev_date.strftime('%Y-%m-%d')}"
    next_callback = f"pod:{next_date.strftime('%Y-%m-%d')}"

    add = [
        InlineKeyboardButton('❤️', callback_data=f'like:{current.strftime("%Y-%m-%d")}'),
        InlineKeyboardButton('🏠', callback_data='home'),
    ]

    return PaginationKeyboard(prev_callback, next_callback, add)
