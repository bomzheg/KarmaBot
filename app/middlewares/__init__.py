# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher

from app.middlewares.config_middleware import ConfigMiddleware
from app.middlewares.db_middleware import DBMiddleware
from app.middlewares.fix_target_middleware import FixTargetMiddleware
from app.models.config import Config
from app.utils.lock_factory import LockFactory
from app.utils.log import Logger

logger = Logger(__name__)


def setup(dispatcher: Dispatcher, lock_factory: LockFactory, config: Config):
    logger.info("Configure middlewares...")
    db_middleware_ = DBMiddleware(lock_factory)
    dispatcher.update.outer_middleware.register(ConfigMiddleware(config))
    dispatcher.errors.outer_middleware.register(ConfigMiddleware(config))
    dispatcher.message.outer_middleware.register(db_middleware_)
    dispatcher.callback_query.outer_middleware.register(db_middleware_)
    dispatcher.message.middleware.register(FixTargetMiddleware(tg_client_config=config.tg_client))
