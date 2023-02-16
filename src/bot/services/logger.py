import logging
import settings

from telegram import Update

from typing import Callable, Any


class MessageLogger:

    def __init__(self, loggger_name: str) -> None:
        """ Setup logger. """
        logger = logging.getLogger(loggger_name)
        file_handler = logging.FileHandler(settings.LOGGING_PATH)
        file_handler.setLevel(settings.LOGGING_LEVEL)
        formatter = logging.Formatter(settings.LOGGING_CONFIG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        self.logger = logger 

    def log(self, method: Callable) -> None:
        """  """
        def wrapper_logger(*args, **kwargs) -> Any:
            update: Update = args[1]
            try:
                message = update.message.text
            except AttributeError:
                message = f'callback: {update.callback_query.data}'
            
            text = f"Message -> {update.effective_user.id} | {message}"
            self.logger.info(text)
            return method(*args, **kwargs)
        return wrapper_logger
