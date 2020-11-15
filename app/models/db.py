from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from loguru import logger
from tortoise import Tortoise, run_async

from app import config
karma_filters = ("-karma", "uc_id")


async def on_startup(_: Dispatcher):
    await db_init()


async def db_init():
    await Tortoise.init(
        db_url=get_db_connect_string(),
        modules={'models': ["app.models"]}
    )


def get_db_connect_string():
    if config.DB_TYPE == 'mysql':
        db_url = (
            f'{config.DB_TYPE}://{config.LOGIN_DB}:{config.PASSWORD_DB}'
            f'@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}'
        )
    elif config.DB_TYPE == 'postgres':
        db_url = (
            f'{config.DB_TYPE}://{config.LOGIN_DB}:{config.PASSWORD_DB}'
            f'@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}'
        )
    elif config.DB_TYPE == 'sqlite':
        db_url = (
            f'{config.DB_TYPE}://{config.DB_PATH}'
        )
    else:
        raise ValueError("DB_TYPE not mysql, sqlite or postgres")
    logger.debug("db url {url}", url=db_url)
    return db_url


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
