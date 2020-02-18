from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from tortoise import Tortoise

from app import config
from app.models import __models__


async def on_startup(dp: Dispatcher):
    await Tortoise.init(
        db_url=f'{config.DB_TYPE}://{config.LOGIN_DB}:{config.PASSWORD_DB}'
               f'@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}',
        modules={'models': __models__}
    )


async def on_shutdown(dp: Dispatcher):
    await Tortoise.close_connections()


def setup(executor: Executor):
    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)


if __name__ == "__main__":
    await Tortoise.generate_schemas()
