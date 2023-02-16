import io
import attrs
import aioredis

from copy import copy
from typing import List
from datetime import datetime

from bot.db import MongoClient
from config import get_redis


@attrs.define
class RedisCache:

    expire: int = attrs.field(default=259200)
    redis: aioredis.Redis = attrs.field( 
        default=get_redis(),
        validator=attrs.validators.instance_of(aioredis.Redis)
    )

    async def get_image(self, date: datetime) -> io.BytesIO | None:
        key = 'image:' + date.strftime('%Y-%m-%d')
        _bytes = await self.redis.get(key)
        if _bytes:
            _bytes = io.BytesIO(_bytes)
        return _bytes

    async def cache_image(self, img: str | bytes | io.BytesIO, date: datetime) -> None:
        key = 'image:' + date.strftime('%Y-%m-%d')
        img = copy(img)
        if isinstance(img, io.BytesIO):
            img = img.read()
        await self.redis.set(key, img, ex=self.expire)

    async def get_favorites(self, user_id: int) -> List[str]:
        key = f'user:favorites:{user_id}'
        favorites: list = await self.redis.lrange(key, 0, -1)
        favorites.reverse()
        return favorites

    async def cache_favorites(self, user_id: int, favorites: List[str]) -> None:
        key = f'user:favorites:{user_id}'
        await self.redis.delete(key)
        await self.redis.lpush(key, favorites)
