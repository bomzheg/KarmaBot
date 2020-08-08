import asyncio

from aiogram import types

from app.filters.karma_change import KarmaFilter, PUNCTUATIONS, PLUS_TRIGGERS, PLUS_EMOJI, MINUS, MINUS_EMOJI, PLUS

plus_texts = (*PLUS_TRIGGERS, *PLUS_EMOJI, PLUS * 2, PLUS * 3, PLUS * 4)
minus_texts = (*MINUS, *MINUS_EMOJI)
punctuations = [*PUNCTUATIONS, ""]


def filter_check(message: types.Message):
    karma_filter = KarmaFilter(karma_change=True)
    return asyncio.run(karma_filter.check(message))
