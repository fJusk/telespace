import logging
import settings

from telegram import __version__ as TG_VERSION

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This bot is not compatible with your current Py-Telegram-Bot version {TG_VERSION}."
    )

logging.basicConfig(
    format=settings.LOGGING_CONFIG, 
    level=settings.LOGGING_LEVEL
)

from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from bot.handlers import *


def main() -> None:

    application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler(StartHandler.command, StartHandler()))
    application.add_handler(CommandHandler(HelpHandler.COMMAND, HelpHandler()))
    application.add_handler(CallbackQueryHandler(FavoritesPaginationHandler(), FavoritesPaginationHandler.callback))
    application.add_handler(CallbackQueryHandler(GeneralHandler(), GeneralHandler.callback))
    application.add_handler(CallbackQueryHandler(RandomPictureHandler(), RandomPictureHandler.callback))
    application.add_handler(CallbackQueryHandler(ManageFavoritesHandler(), ManageFavoritesHandler.callback))
    application.add_handler(CallbackQueryHandler(PaginationViewHandler(), PaginationViewHandler.callback))

    application.run_polling()


if __name__ == "__main__":
    main()
