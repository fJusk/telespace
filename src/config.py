import aioredis

from aiohttp import ClientSession

try:
    from settings import REDIS_CONFIG
except ImportError:
    raise ImportError('Cant import REDIS_CONFIG from root settings.')

_session = ClientSession()

def get_session() -> ClientSession:
    return _session

def get_redis() -> aioredis.Redis:
    return aioredis.from_url(**REDIS_CONFIG)
