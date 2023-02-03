from aiogram import Dispatcher

from . import base
from . import change_karma
from . import errors
from . import karma
from . import moderator
from . import settings


def setup(dp: Dispatcher):
    errors.setup(dp)
    dp.include_router(base.router)
    dp.include_router(change_karma.router)
    dp.include_router(karma.router)
    dp.include_router(moderator.router)
    dp.include_router(settings.router)
