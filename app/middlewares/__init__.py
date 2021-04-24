# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher

from app.middlewares.db_middleware import DBMiddleware
from app.models.config import Config
from app.utils.log import Logger


logger = Logger(__name__)


def setup(dispatcher: Dispatcher, config: Config):
    logger.info("Configure middlewares...")
    dispatcher.middleware.setup(DBMiddleware(tg_client_config=config.tg_client))
