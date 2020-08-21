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
        karma_change, comment = get_karma_trigger(message.text or message.sticker.emoji or "")
        if karma_change is None:
            return {}
        rez = {'karma': {'karma_change': karma_change, 'comment': comment}}
        return rez


def get_karma_trigger(text: str) -> typing.Tuple[typing.Optional[int], str]:
    """
    :return: tuple (how_change, comment)
        how_change:
            if contain trigger + karma +1
            if contain trigger - karma -1
            if contain no karma trigger None
        comment: all text after trigger
    :param text:
    """
    possible_trigger, comment = get_first_word(text)
    if has_plus_karma(possible_trigger):
        return +1, comment
    possible_trigger, comment = get_first_line(text)
    if has_minus_karma(possible_trigger):
        return -1, comment
    return None, ""


def get_first_word(text: str) -> typing.Tuple[str, str]:
    args = text.split(maxsplit=1)

    possible_trigger = args[0]
    if len(args) > 1:
        comment = args[1].splitlines()
    else:
        comment = []

    return possible_trigger.lower().rstrip(PUNCTUATIONS), " ".join(comment)


def has_plus_karma(word: str) -> bool:
    if len(word) == 0:
        return False
    if len(word) > 1 and word[1:] == word[:-1] and word[1] == PLUS:  # contains only ++..+
        return True
    return word in PLUS_TRIGGERS or word[0] in PLUS_EMOJI


def has_minus_karma(text: str) -> bool:
    return text in MINUS or (text.split(maxsplit=1)[0] == text and text[0] in MINUS_EMOJI)


def get_first_line(text: str) -> typing.Tuple[str, str]:
    args = text.splitlines()

    possible_trigger = args[0]
    if len(args) > 1:
        comment = args[1:]
    else:
        comment = []
    return possible_trigger, " ".join(comment)
