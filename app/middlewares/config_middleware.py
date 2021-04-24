from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types.base import TelegramObject

from app.models.config import Config
from app.utils.log import Logger


logger = Logger(__name__)


class ConfigMiddleware(LifetimeControllerMiddleware):
    def __init__(self, config: Config):
        super(ConfigMiddleware, self).__init__()
        self.config = config

    async def pre_process(self, obj: TelegramObject, data: dict, *args):
        data["config"]: Config = self.config
