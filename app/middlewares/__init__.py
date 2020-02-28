# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from loguru import logger

from app.middlewares.acl import ACLMiddleware


def setup(dispatcher: Dispatcher):
    logger.info("Configure middlewares...")
    #dispatcher.middleware.setup(LoggingMiddleware("bot"))
    dispatcher.middleware.setup(ACLMiddleware())
