import io
import attrs

from telegram import InputMediaPhoto

from typing import List
from datetime import datetime

from bot.db import MongoClient

from spaceapi import SpaceAPI
from spaceapi.schemas import APODResponse

from .cache import RedisCache


@attrs.define
class PhotoLoader:

    client_api: SpaceAPI = attrs.field(validator=attrs.validators.instance_of(SpaceAPI))
    db: MongoClient = attrs.field(
        validator=attrs.validators.instance_of(MongoClient),
        default=MongoClient()
    )
    cache: RedisCache = attrs.field(default=RedisCache())

    @classmethod
    def generate_text(cls, data: APODResponse) -> str:
        text = data.explanation.split('.')
        expl = ''
        for sentence in text:
            if len(sentence + expl) < 1000:
                expl += sentence
            else: 
                break
        return f"{data.title}\n\n{expl}\n\n{data.date.strftime('%Y-%m-%d')}"

    async def get_or_call(self, data: APODResponse, date: datetime = datetime.now()) -> InputMediaPhoto:
        """ Get picture from Redis or call API """
        _bytes = await self.cache.get_image(date)
        if _bytes is None:
            resp = await self.client_api.image_by_date(date)
            _bytes = resp.img
            await self.cache.cache_image(_bytes, date)
        _file = io.BufferedReader(_bytes)
        return InputMediaPhoto(_file, self.generate_text(data))

    async def random_picture(self) -> tuple:
        data, = await self.client_api.random(length=1)
        _file = io.BufferedReader(data.img)
        return data, InputMediaPhoto(_file, self.generate_text(data))

    async def load_favorites(self, user_id: int, update: bool = False) -> List[str]:
        favorites = await self.cache.get_favorites(user_id)
        if len(favorites) == 0:
            user = self.db.get_user(user_id)
            favorites = user.favorites
        return favorites
