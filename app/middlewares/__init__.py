# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher
from loguru import logger

from app.middlewares.acl import ACLMiddleware
from app.models.config import Config


def setup(dispatcher: Dispatcher, config: Config):
    logger.info("Configure middlewares...")
    dispatcher.middleware.setup(ACLMiddleware(tg_client_config=config.tg_client))
