import typing
from dataclasses import dataclass

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from app.config import PLUS, PLUS_TRIGGERS, MINUS, PLUS_EMOJI, MINUS_EMOJI

PUNCTUATIONS = ",.!"


@dataclass
class KarmaFilter(BoundFilter):
    """
    Filtered message should be change karma
    """

    key = "karma_change"

    karma_change: bool

    async def check(self, message: types.Message) -> typing.Dict[str, typing.Dict[str, int]]:
        karma_change = get_karma_trigger(message.text or message.sticker.emoji or None)
        if karma_change is None:
            return {}
        target_user = get_target_user(message)
        if target_user is None:
            return {}
        if target_user.is_bot:
            return {}
        rez = {'karma': {'user': target_user, 'karma_change': karma_change}}
        return rez


def get_karma_trigger(text: str) -> typing.Optional[int]:
    """
    if contain trigger + karma return +1
    if contain trigger - karma return -1
    if contain no karma trigger return None
    :param text:
    :return:
    """
    if has_plus_karma(get_first_word(text)):
        return +1
    if has_minus_karma(text):
        return -1
    return None


def get_first_word(text: str) -> str:
    return text.split(maxsplit=1)[0].lower().rstrip(PUNCTUATIONS)


def has_plus_karma(word: str) -> bool:
    if len(word) == 0:
        return False
    if len(word) > 1 and word[1:] == word[:-1] and word[1] == PLUS:  # contains only ++..+
        return True
    return word in PLUS_TRIGGERS or word[0] in PLUS_EMOJI


def has_minus_karma(text: str) -> bool:
    return text in MINUS or (text.split(maxsplit=1)[0] == text and text[0] in MINUS_EMOJI)


def get_target_user(message: types.Message) -> typing.Optional[types.user.User]:
    """
    Target user can be take from reply or by mention
    :param message:
    :return:
    """

    author_user = message.from_user

    target_user = get_replyed_user(message)
    if has_target_user(target_user, author_user):
        return target_user

    target_user = get_mentioned_user(message)
    if has_target_user(target_user, author_user):
        return target_user
    return None


def has_target_user(target_user: types.User, author_user: types.User):
    """

    :return: True if target_user exist, not is author and not bot
    """

    def is_one_user(user_1: types.User, user_2: types.User):
        return (user_1.id is not None and user_1.id == user_2.id) \
               or user_1.username is not None and user_1.username == user_2.username

    return target_user is not None \
        and not is_one_user(author_user, target_user)\
        and not target_user.is_bot
    #   and not is_bot_username(target_user.username)
    # don't check is_bot_username because user can have username like @user_bot


def get_mentioned_user(message: types.Message) -> typing.Optional[types.User]:
    if not message.text:
        return None
    if not message.entities:
        return None
    for ent in message.entities:
        if ent.type == "text_mention":
            return ent.user
        elif ent.type == "mention":
            username = ent.get_text(message.text).lstrip("@")
            return types.User(username=username)
    return None


def get_replyed_user(message: types.Message) -> typing.Optional[types.User]:
    if message.reply_to_message:
        return message.reply_to_message.from_user
    return None


def is_bot_username(username: str):
    return username is not None and username[-2:] == "bot"
