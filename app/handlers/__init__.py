from aiogram import Dispatcher, Bot

from . import base
from . import change_karma
from . import errors
from . import karma
from . import moderator
from . import settings
from ..models.config import Config


def setup(dp: Dispatcher, bot: Bot, config: Config):
    errors.setup(dp, bot, config)
    dp.include_router(base.router)
    dp.include_router(change_karma.router)
    dp.include_router(karma.router)
    dp.include_router(moderator.router)
    dp.include_router(settings.router)
