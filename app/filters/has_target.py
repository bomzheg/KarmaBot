import typing
from dataclasses import dataclass

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from app.services.find_target_user import get_target_user


@dataclass
class HasTargetFilter(BoundFilter):
    key = "has_target"
    has_target: typing.Optional[typing.Dict[str, bool]]

    def __post_init__(self):
        if self.has_target is True:
            self.has_target = {}

    async def check(self, message: types.Message) -> typing.Dict[str, types.User]:
        can_be_same = self.has_target.get("can_be_same", False)
        can_be_bot = self.has_target.get("can_be_bot", False)
        target_user = get_target_user(message, can_be_same, can_be_bot)
        if target_user is None:
            return {}
        rez = {'target': target_user}
        return rez
