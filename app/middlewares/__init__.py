# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher
from loguru import logger

from app.middlewares.acl import ACLMiddleware


def setup(dispatcher: Dispatcher):
    logger.info("Configure middlewares...")
    dispatcher.middleware.setup(ACLMiddleware())
