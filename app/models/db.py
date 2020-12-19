from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from loguru import logger
from tortoise import Tortoise, run_async

from app import config
karma_filters = ("-karma", "uc_id")


async def on_startup(_: Dispatcher):
    await db_init()


async def db_init():
    await Tortoise.init(config=config.TORTOISE_ORM)
    logger.info("database configured")


async def on_shutdown(_: Dispatcher):
    await Tortoise.close_connections()


def setup(executor: Executor):
    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)


async def generate_schemas_db():
    await db_init()
    await Tortoise.generate_schemas()


def generate_schemas():
    run_async(generate_schemas_db())
