import asyncio
from aiogram import types
from app.filters.karma_change import KarmaFilter, PUNCTUATIONS, PLUS, PLUS_EMOJI, MINUS, MINUS_EMOJI
plus_texts = (*PLUS, *PLUS_EMOJI, PLUS[0]*2, PLUS[0]*3, PLUS[0]*4)
minus_texts = (*MINUS, *MINUS_EMOJI)
punctuations = [*PUNCTUATIONS, ""]


def filter_check(message: types.Message):
    karma_filter = KarmaFilter(karma_change=True)
    return asyncio.run(karma_filter.check(message))
