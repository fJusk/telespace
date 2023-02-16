from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes

from datetime import datetime

from bot.db import MongoClient
from bot.services import MessageLogger

from settings import LOGO_PATH
from bot.keyboards import generate_general_kb


logger = MessageLogger(__name__)

db = MongoClient()


class StartHandler:
    command: str = 'start'

    @logger.log
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        db.get_or_create(user_id)

        text = "Привет!\n\nЭтот бот позволит тебе увидеть космос. Нажми на кнопку "\
            "Картинка дня и ты все увидишь."

        await update.effective_user.send_photo(LOGO_PATH, text, reply_markup=generate_general_kb(date=datetime.now()))


class GeneralHandler:
    callback: str = 'home'

    @logger.log
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.callback_query.answer()
        text = 'Главное меню.'
        await update.callback_query.edit_message_media(
            InputMediaPhoto(open(LOGO_PATH, mode='rb'), caption=text),
            reply_markup=generate_general_kb(date=datetime.now())
        )


class HelpHandler:
    COMMAND: str = 'help'

    @logger.log
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = "Что-то не получается? Давай попробуем еще раз.\n\n"
        clues = [
            '/start - если что-то пошло не так.',
            '/help - помощь.',
            'Кнопка "Картинка дня" - показывает текущую картинку дня и позволяет пролистывать картинки.',
            'Кнопка "Избранные" - показывает твои израбнные картинки.',
            'Кнопка "Случайная картинка" - показывает случайную картинку.'
        ]
        text += '\n'.join(clues)

        await update.effective_user.send_message(text)
