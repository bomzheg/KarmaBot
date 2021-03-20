from dataclasses import dataclass
from typing import Iterable

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from app.models.db import User


@dataclass
class IsSuperuserFilter(BoundFilter):
    key = "is_superuser"
    is_superuser: bool = None

    async def check(self, superusers: Iterable[int], event) -> bool:
        data = ctx_data.get()
        user: User = data["user"]
        return user.tg_id in superusers
