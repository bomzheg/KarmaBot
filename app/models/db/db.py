from functools import partial

from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from tortoise import Tortoise, run_async

from app.models.config import DBConfig
from app.utils.log import Logger


logger = Logger(__name__)
__models__ = ['app.models.db']
karma_filters = ("-karma", "uc_id")


async def on_startup(_: Dispatcher, db_config: DBConfig):
    await db_init(db_config)


async def db_init(db_config: DBConfig):
    db_url = db_config.create_url_config()
    logger.info("connecting to db {db_url}", db_url=db_url)
    await Tortoise.init(
        db_url=db_url,
        modules={'models': __models__}
    )


async def on_shutdown(_: Dispatcher):
    await Tortoise.close_connections()


def setup(executor: Executor, db_config: DBConfig):
    executor.on_startup(partial(on_startup, db_config=db_config))
    executor.on_shutdown(on_shutdown)


async def generate_schemas_db(db_config: DBConfig):
    await db_init(db_config)
    await Tortoise.generate_schemas()


def generate_schemas(db_config: DBConfig):
    run_async(generate_schemas_db(db_config))
