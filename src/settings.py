import os
import logging

from pathlib import Path

# General
BASE_DIR = Path(Path.cwd(), 'src')
STATIC_DIR = BASE_DIR / Path('bot', 'static')

LOGO_PATH = STATIC_DIR / Path('logo.jpg')

# Secure warning
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
NASA_TOKEN = os.getenv('NASA_TOKEN')

# Logging
LOGGING_CONFIG = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGGING_LEVEL = logging.INFO
LOGGING_PATH = BASE_DIR / Path('bot', 'logs', 'messages.log')

# dbs
REDIS_CONFIG = {
    'url': 'redis://localhost',
    'username': os.getenv('REDIS_USERNAME'),
    'password': os.getenv('REDIS_PASSWORD')
}

MONGO_CONFIG = {
    'url': os.getenv('MONGO_URL'),
    'db': 'tg_bot',
}
