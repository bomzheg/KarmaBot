# partially from https://github.com/aiogram/bot
from aiogram import Bot, Dispatcher, types

from app.config import load_config
from app.models.config import Config
from app.utils.log import Logger


logger = Logger(__name__)
current_config = load_config()

bot = Bot(current_config.bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=current_config.storage.create_storage())


def setup(config: Config):
    from app import filters
    from app import middlewares
    from app.utils import executor
    logger.debug(f"As application dir using: {config.app_dir}")

    middlewares.setup(dp, config)
    filters.setup(dp, config)
    executor.setup(config)

    logger.info("Configure handlers...")
    # noinspection PyUnresolvedReferences
    import app.handlers
