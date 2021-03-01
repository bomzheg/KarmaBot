from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from loguru import logger
from tortoise import Tortoise, run_async

from app import config


__models__ = ['app.models.db']
karma_filters = ("-karma", "uc_id")


async def on_startup(_: Dispatcher):
    await db_init()


async def db_init():
    db_url = config.db_config.create_url_config()
    logger.info("connecting to db {db_url}", db_url=db_url)
    await Tortoise.init(
        db_url=db_url,
        modules={'models': __models__}
    )


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
