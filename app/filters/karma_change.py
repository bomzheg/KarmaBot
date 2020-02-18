from dataclasses import dataclass
from typing import Union, Dict

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


@dataclass
class KarmaFilter(BoundFilter):
    """
    Filtered message should be change karma
    """

    key = "karma_change"

    karma_change: bool

    async def check(self, message: types.Message) -> Union[bool, Dict[str, Dict[str, int]]]:
        karma_change = await get_karma_trigger(message.text)
        if karma_change is None:
            return False
        target_user = await get_target_user(message)
        if target_user is None:
            return False
        return {'karma': {'user': target_user, 'karma_change': karma_change}}


async def get_karma_trigger(text: str) -> Union[int, None]:
    """
    if contain trigger + karma return +1
    if contain trigger - karma return -1
    if contain no karma trigger return None
    :param text:
    :return:
    """
    if has_plus_karma(text):
        return +1
    if has_minus_karma(text):
        return -1
    return None


def has_plus_karma(text: str) -> bool:
    return text == '+' or text.lower == 'спасибо' or text == '👍'


def has_minus_karma(text: str) -> bool:
    return text == '-' or text == '👎'


async def get_target_user(message: types.Message) -> Union[types.user, None]:
    """
    Target user can be take from reply or by mention
    :param message:
    :return:
    """
    if message.reply_to_message:
        return message.reply_to_message.from_user
    mentioned_user = get_mentioned_user(message)
    return mentioned_user


def get_mentioned_user(message: types.Message) -> Union[int, None]:
    return False
