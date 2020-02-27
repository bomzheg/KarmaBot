from dataclasses import dataclass
from typing import Union, Dict
from loguru import logger
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from app.misc import bot


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
        if target_user.is_bot:
            return False
        rez = {'karma': {'user': target_user, 'karma_change': karma_change}}
        return rez


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

THANK = 'спасибо'
def has_plus_karma(text: str) -> bool:
    if text.startswith('+', '👍'):
        return True
    if len(text) > len(THANK) and text[:7].lower == THANK:
        return True


def has_minus_karma(text: str) -> bool:
    return text == '-' or text == '👎'


async def get_target_user(message: types.Message) -> Union[types.user.User, None]:
    """
    Target user can be take from reply or by mention
    :param message:
    :return:
    """
    def has_target_user():
        return target_user is not None and target_user != author_user

    author_user = message.from_user.id

    target_user = get_replyed_user(message)
    if has_target_user():
        return target_user
    
    target_user = get_mentioned_user(message)
    if has_target_user():
        return target_user
    return None

def get_mentioned_user(message: types.Message) -> Union[types.User, None]:
    if not message.text:
        return None
    if not message.entities:
        return None
    for ent in message.entities:
        if ent.type == "text_mention":
            return ent.user
        elif ent.type == "mention":
            # username like '@user'
            username = message.text[ent.offset:ent.offset + ent.length]
            return types.User(username=username[1:])
    return None


def get_replyed_user(message: types.Message) -> Union[types.User, None]:
    if message.reply_to_message:
        return message.reply_to_message.from_user
    return None
