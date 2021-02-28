from dataclasses import dataclass

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from app import config
from app.models import User


@dataclass
class IsSuperuserFilter(BoundFilter):
    key = "is_superuser"
    is_superuser: bool

    async def check(self, obj) -> bool:
        data = ctx_data.get()
        user: User = data["user"]
        return user.tg_id in config.SUPERUSERS
