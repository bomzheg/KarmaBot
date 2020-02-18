from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from loguru import logger

from app import config

app_dir: Path = Path(__file__).parent.parent

bot = Bot(config.TEST_BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
dp = Dispatcher(bot, storage=storage)


def setup():
    from app import filters
    from app import middlewares
    from app.utils import executor
    logger.debug(f"As application dir using: {app_dir}")

    middlewares.setup(dp)
    filters.setup(dp)
    executor.setup()

    logger.info("Configure handlers...")
    # noinspection PyUnresolvedReferences
    import app.handlers
