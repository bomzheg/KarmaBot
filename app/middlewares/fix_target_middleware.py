from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.models.config import TgClientConfig
from app.services.find_target_user import get_db_user_by_tg_user


class FixTargetMiddleware(BaseMiddleware):
    def __init__(self, tg_client_config: TgClientConfig):
        super(FixTargetMiddleware, self).__init__()
        self.tg_client_config = tg_client_config

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if target := data.get("target", None):
            target = await get_db_user_by_tg_user(target, self.tg_client_config)
            data["target"] = target
        return await handler(event, data)
