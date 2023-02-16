from pydantic import BaseModel, validator

from typing import Iterable, BinaryIO

from datetime import datetime


class Request(BaseModel):
    method: str 
    url: str = None
    force: bool = False
    kwargs: dict = {}


class APODRequest(BaseModel):
    date: str | datetime = ''
    start_date: str | datetime = ''
    end_date: str | datetime = ''
    count: int | str = ''
    thumbs: bool | str = ''
    api_key: str = 'DEMO_KEY'

    @validator('date', 'start_date', 'end_date')
    def validate_date(cls, value: datetime) -> str:
        return value.strftime('%Y-%m-%d')


class APODResponse(BaseModel):
    copyright: str = None
    date: datetime | str 
    explanation: str 
    hdurl: str 
    media_type: str
    service_version: str
    title: str
    url: str
    img: bytes = None

    @validator('date')
    def validate_date(cls, value) -> datetime:
        return datetime.fromisoformat(value)
