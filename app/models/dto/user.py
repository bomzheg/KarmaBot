from dataclasses import dataclass

from aiogram import types


@dataclass
class TargetUser:
    id: int | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_bot: bool | None = None

    @classmethod
    def from_aiogram(cls, user: types.User):
        return cls(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_bot=user.is_bot,
        )
