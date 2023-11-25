from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services.find_target_user import get_db_user_by_tg_user
from app.services.user_getter import UserGetter


class FixTargetMiddleware(BaseMiddleware):
    def __init__(self, user_getter: UserGetter):
        super().__init__()
        self.user_getter = user_getter

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if target := data.get("target", None):
            target = await get_db_user_by_tg_user(
                target, self.user_getter, data["user_repo"]
            )
            data["target"] = target
        return await handler(event, data)
