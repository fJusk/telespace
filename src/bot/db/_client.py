import attrs
import pymongo

from datetime import datetime

from settings import MONGO_CONFIG

from .models import User


@attrs.define
class MongoClient:

    client = attrs.field(
        default=pymongo.MongoClient(MONGO_CONFIG['url']),
        validator=attrs.validators.instance_of(pymongo.MongoClient)
    )
    db_name = attrs.field(default='tg_bot')

    def get_user(self, user_id: int) -> User:
        db = self.client[self.db_name][User._collection]
        user_data = db.find_one(filter={'_id': user_id})
        if user_data is None:
            return User(_id=user_id)
        return User(**user_data)

    def get_or_create(self, user_id: int) -> User:
        db = self.client[self.db_name][User._collection]
        user_data = {'_id': user_id}
        user = db.find_one(user_data)
        if user is None:
            db.insert_one(user_data)
            return User(**user_data)
        return User(**user)

    def add_favorite(self, user_id: int, date: datetime) -> None:
        db = self.client[self.db_name][User._collection]
        user = self.get_user(user_id)
        favorites = user.favorites
        if date.strftime('%Y-%m-%d') in favorites:
            return False
        user_data = {'_id': user_id}
        update_data = {'$push': {'favorites': date.strftime('%Y-%m-%d')}}
        db.update_one(user_data, update_data)
        return True

    def pop_favorite(self, user_id: int, index: int) -> None:
        db = self.client[self.db_name][User._collection]
        user_data = {'_id': user_id}
        user = self.get_user(user_id)
        value = user.favorites.pop(index)
        update_data = {'$pull': {'favorites': value}}
        db.update_one(user_data, update_data)
