# partially from https://github.com/aiogram/bot
from aiogram import Bot, Dispatcher, Router

from app.config import load_config
from app.models.config import Config
from app.utils.log import Logger


logger = Logger(__name__)
current_config = load_config()

bot = Bot(current_config.bot_token, parse_mode="HTML")
dp = Dispatcher(storage=current_config.storage.create_storage())
router = Router(name=__name__)


def setup(config: Config):
    from app import middlewares
    logger.debug(f"As application dir using: {config.app_dir}")

    middlewares.setup(dp, config)

    logger.info("Configure handlers...")
    # noinspection PyUnresolvedReferences
    import app.handlers
    dp.include_router(router)
