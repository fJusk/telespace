from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from datetime import datetime

from bot.db import MongoClient
from bot.services import MessageLogger, PhotoLoader
from bot.keyboards import generate_photo_pagination, PaginationKeyboard,\
    generate_random_kb

from spaceapi import SpaceAPI
from config import get_session
from settings import NASA_TOKEN

# Init logger
logger = MessageLogger(__name__)

# Create photo service
client = SpaceAPI(session=get_session(), api_key=NASA_TOKEN)
photo_service = PhotoLoader(client)

# db
db = MongoClient()


class PaginationViewHandler:
    callback = '^pod:\d{4}-\d{2}-\d{2}$'

    @logger.log
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.callback_query.answer()
        date = datetime.fromisoformat(update.callback_query.data.split(':')[-1])
        data = await client.apod(date=date)
        media = await photo_service.get_or_call(data=data, date=date)
        pagination = generate_photo_pagination(date)
        await update.callback_query.edit_message_media(
            media=media,
            reply_markup=pagination.keyboard
        )


class FavoritesPaginationHandler:
    callback = '^favorites:\d+$'

    @logger.log
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        index = int(update.callback_query.data.split(':')[-1])
        query = await photo_service.load_favorites(update.effective_user.id, index == 0)
        if len(query) == 0:
            await update.callback_query.answer('У вас нет фото в избранных!')
            return

        picture_date = datetime.fromisoformat(query[index])
        apod = await photo_service.client_api.apod(date=picture_date)
        media = await photo_service.get_or_call(apod, date=picture_date)

        next_index = index + 1 if index + 1 < len(query) else 0
        prev_index = index - 1 if index - 1 > -1 else len(query) - 1

        pagination = PaginationKeyboard(
            prev_callback=f'favorites:{prev_index}',
            next_callback=f'favorites:{next_index}',
            add=[
                InlineKeyboardButton('💔', callback_data=f'unlike:{index}'),
                InlineKeyboardButton('🏠', callback_data='home'),
            ]
        )
        try:
            await update.callback_query.edit_message_media(
                media=media,
                reply_markup=pagination.keyboard
            )
        except BadRequest:
            await update.callback_query.answer('У вас одно фото в избранных!')


class ManageFavoritesHandler:
    callback = '^(like|unlike):(\d{4}-\d{2}-\d{2}|\d+)$'

    @logger.log
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        action, img_data = update.callback_query.data.split(':')
        user_id = update.effective_user.id

        match action:

            case 'like':
                try:
                    date = datetime.fromisoformat(img_data)
                    result = db.add_favorite(user_id, date)
                    if not result:
                        await update.callback_query.answer('Фото уже в избранном!')
                except ValueError:
                    await update.callback_query.answer('Что-то пошло не так! Попробуйте еще раз.')
                else:
                    await update.callback_query.answer('Фото добавлено в избранные!')

            case 'unlike':
                if not img_data.isdigit():
                    await update.callback_query.answer('Что-то пошло не так! Попробуйте еще раз.')
                    return
                db.pop_favorite(user_id, int(img_data))
                await update.callback_query.answer('Фото удалено из избранных.')


class RandomPictureHandler:
    callback = '^picture:random$'

    @logger.log
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.callback_query.answer('Пожалуйста, подождите. Действие может занимать некоторое время!')
        data, media = await photo_service.random_picture()
        keyboard = generate_random_kb(data.date)
        await update.callback_query.edit_message_media(
            media=media,
            reply_markup=keyboard
        )
