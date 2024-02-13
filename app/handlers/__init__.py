from aiogram import Bot, Dispatcher

from ..models.config import Config
from . import (
    base,
    change_karma,
    chat_rules,
    errors,
    karma,
    moderator,
    settings,
    superuser,
)


def setup(dp: Dispatcher, bot: Bot, config: Config):
    errors.setup(dp, bot, config)
    dp.include_router(base.router)
    dp.include_router(change_karma.router)
    dp.include_router(karma.router)
    dp.include_router(moderator.router)
    dp.include_router(settings.router)
    dp.include_router(superuser.setup_superuser(config))
    dp.include_router(chat_rules.setup())
