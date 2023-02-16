from pydantic import BaseModel, PrivateAttr

from typing import List


class User(BaseModel):
    _collection: str = 'user'

    _id: int 
    favorites: List[str] = []
