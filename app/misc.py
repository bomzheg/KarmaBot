# partially from https://github.com/aiogram/bot
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger

from app import config

app_dir: Path = Path(__file__).parent.parent

bot = Bot(config.TEST_BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


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
