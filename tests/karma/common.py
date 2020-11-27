import asyncio

from aiogram import types

from app.filters.karma_change import (
    KarmaFilter, PUNCTUATIONS, PLUS_TRIGGERS, PLUS_EMOJI, MINUS_TRIGGERS, MINUS_EMOJI, PLUS, INF
)

plus_texts = (*PLUS_TRIGGERS, *PLUS_EMOJI, PLUS * 2, PLUS * 3, PLUS * 4)
minus_texts = (*MINUS_TRIGGERS, *MINUS_EMOJI)
punctuations = [*PUNCTUATIONS, ""]
SPACES = (" ", "\t", "\n", "\r")


def filter_check(message: types.Message):
    karma_filter = KarmaFilter(karma_change=True)
    return asyncio.run(karma_filter.check(message))


__all__ = [
    KarmaFilter, PUNCTUATIONS, PLUS_TRIGGERS, PLUS_EMOJI, MINUS_TRIGGERS, MINUS_EMOJI, PLUS, INF,
    plus_texts, minus_texts, punctuations, SPACES, filter_check
]
