import typing
from dataclasses import dataclass

from aiogram import types
from aiogram.filters import BaseFilter

from app.config.karmic_triggers import (
    PLUS,
    PLUS_TRIGGERS,
    PLUS_EMOJI,
    MINUS,
    MINUS_EMOJI,
    MINUS_TRIGGERS,
)
from app.infrastructure.database.models import ChatSettings

PUNCTUATIONS = ",.!)"
INF = float('inf')


@dataclass
class KarmaFilter(BaseFilter):
    """
    Filtered message should be change karma
    """

    async def __call__(
        self, message: types.Message, chat_settings: ChatSettings,
    ) -> dict[str, dict[str, float]]:
        if chat_settings is None or not chat_settings.karma_counting:
            return {}
        return await check(message)


async def check(message: types.Message) -> dict[str, dict[str, float]]:
    possible_trigger_text = message.text or message.caption
    if possible_trigger_text is None and message.sticker:
        possible_trigger_text = message.sticker.emoji or None
    karma_change, comment = get_karma_trigger(possible_trigger_text)
    if karma_change is None:
        return {}
    rez = {'karma': {'karma_change': karma_change, 'comment': comment}}
    return rez


def get_karma_trigger(text: str) -> tuple[typing.Optional[float], str]:
    """
    :return: tuple (how_change, comment)
        how_change: shows how much to change karma wants user
        comment: all text after trigger
    :param text:
    """
    if text is not None:
        possible_trigger, comment = get_first_word(text)

        changer = has_plus_karma(possible_trigger)
        if changer:
            return changer, comment
        changer = has_minus_karma(possible_trigger)
        if changer:
            return changer, comment
    return None, ""


def get_first_word(text: str) -> tuple[str, str]:
    args = text.split(maxsplit=1)

    possible_trigger = args[0]
    if len(args) > 1:
        comment = args[1].splitlines()
    else:
        comment = []

    return possible_trigger.lower().rstrip(PUNCTUATIONS), " ".join(comment)


def has_plus_karma(possible_trigger: str) -> typing.Optional[float]:
    if len(possible_trigger) == 0:
        # blank line has no triggers
        return None
    if all([
        len(possible_trigger) > 1,
        possible_trigger[1:] == possible_trigger[:-1],
        possible_trigger[0:len(PLUS)] == PLUS
    ]):
        # contains only ++..+
        return INF
    if possible_trigger in PLUS_TRIGGERS:
        return INF
    if possible_trigger[0] in PLUS_EMOJI:
        return INF
    if possible_trigger[0:len(PLUS)] == PLUS:
        try:
            return +int(possible_trigger[len(PLUS):])
        except ValueError:
            pass
    return None


def has_minus_karma(possible_trigger: str) -> typing.Optional[float]:
    if len(possible_trigger) == 0:
        return None
    if possible_trigger in MINUS_TRIGGERS:
        return -INF
    # TODO: I think next function run:
    #  has_spaces(possible_trigger)
    #  will never be true. Maybe we can remove it from condition
    if not has_spaces(possible_trigger) and possible_trigger[0] in MINUS_EMOJI:
        return -INF
    if possible_trigger[0:len(MINUS)] == MINUS:
        try:
            return -int(possible_trigger[len(MINUS):])
        except ValueError:
            pass
    return None


def get_first_line(text: str) -> tuple[str, str]:
    args = text.splitlines()

    possible_trigger = args[0]
    if len(args) > 1:
        comment = args[1:]
    else:
        comment = []
    return possible_trigger, " ".join(comment)


def has_spaces(text: str) -> bool:
    return text.split(maxsplit=1)[0] != text
