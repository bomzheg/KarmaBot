# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher

from app.middlewares.config_middleware import ConfigMiddleware
from app.middlewares.db_middleware import DBMiddleware
from app.middlewares.fix_target_middleware import FixTargetMiddleware
from app.models.config import Config
from app.services.user_getter import UserGetter
from app.utils.log import Logger

logger = Logger(__name__)


def setup(dispatcher: Dispatcher, user_getter: UserGetter, config: Config):
    logger.info("Configure middlewares...")
    db_middleware_ = DBMiddleware()
    dispatcher.update.outer_middleware.register(ConfigMiddleware(config))
    dispatcher.errors.outer_middleware.register(ConfigMiddleware(config))
    dispatcher.message.outer_middleware.register(db_middleware_)
    dispatcher.callback_query.outer_middleware.register(db_middleware_)
    dispatcher.message.middleware.register(FixTargetMiddleware(user_getter))
