import typing
from dataclasses import dataclass

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from app.config import PLUS, PLUS_TRIGGERS, PLUS_EMOJI, MINUS, MINUS_EMOJI, MINUS_TRIGGERS

PUNCTUATIONS = ",.!"
INF = float('inf')


@dataclass
class KarmaFilter(BoundFilter):
    """
    Filtered message should be change karma
    """

    key = "karma_change"

    karma_change: bool

    async def check(self, message: types.Message) -> typing.Dict[str, typing.Dict[str, float]]:
        karma_change, comment = get_karma_trigger(message.text or message.sticker.emoji or "")
        if karma_change is None:
            return {}
        rez = {'karma': {'karma_change': karma_change, 'comment': comment}}
        return rez


def get_karma_trigger(text: str) -> typing.Tuple[typing.Optional[float], str]:
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
    changer = has_plus_karma(possible_trigger)
    if changer:
        return changer, comment
    possible_trigger, comment = get_first_line(text)
    changer = has_minus_karma(possible_trigger)
    if changer:
        return changer, comment
    return None, ""


def get_first_word(text: str) -> typing.Tuple[str, str]:
    args = text.split(maxsplit=1)

    possible_trigger = args[0]
    if len(args) > 1:
        comment = args[1].splitlines()
    else:
        comment = []

    return possible_trigger.lower().rstrip(PUNCTUATIONS), " ".join(comment)


def has_plus_karma(word: str) -> typing.Optional[float]:
    if len(word) == 0:
        return None
    if len(word) > 1 and word[1:] == word[:-1] and word[0:len(PLUS)] == PLUS:  # contains only ++..+
        return INF
    if word in PLUS_TRIGGERS:
        return INF
    if word[0] in PLUS_EMOJI:
        return INF
    if word[0:len(PLUS)] == PLUS and word[len(PLUS):].isdecimal():
        return +int(word[len(PLUS):])
    return None


def has_minus_karma(first_line: str) -> typing.Optional[float]:
    if len(first_line) == 0:
        return None
    if first_line in MINUS_TRIGGERS:
        return -INF
    if not has_spaces(first_line) and first_line[0] in MINUS_EMOJI:
        return -INF
    if first_line[0:len(MINUS)] == MINUS and first_line[len(MINUS):].isdecimal():
        return -int(first_line[len(MINUS):])
    return None


def get_first_line(text: str) -> typing.Tuple[str, str]:
    args = text.splitlines()

    possible_trigger = args[0]
    if len(args) > 1:
        comment = args[1:]
    else:
        comment = []
    return possible_trigger, " ".join(comment)


def has_spaces(text: str) -> bool:
    return text.split(maxsplit=1)[0] != text
