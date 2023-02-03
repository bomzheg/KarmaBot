import typing
from datetime import datetime
from random import choice
from string import ascii_letters

from aiogram import types


def get_next_word_parts(
        first_word: str,
        punctuations: typing.Iterable[str],
        spaces: typing.Iterable[str]
) -> typing.List[typing.List[str]]:
    """
    собрать список из списков [first_word, знак препинания, пробельный символ, сгенерированные следующее слово]
    """
    rez = []
    for punctuation in punctuations:
        for space in spaces:
            for count in (0, 1, 2, 5, 20):
                rez.append([first_word, punctuation, space, get_next_words(count)])
    return rez


def generate_phrases_next_word(
        first_word: str,
        punctuations: typing.Iterable[str],
        spaces: typing.Iterable[str]
) -> typing.List[str]:
    """
    get string like %karma_trigger%%punctuation%%space%%next_words%
    """
    precursors_lists = get_next_word_parts(first_word, punctuations, spaces)
    return ["".join(precursors_list) for precursors_list in precursors_lists]


def get_wrong_next_word_parts(first_word: str, punctuations: typing.Iterable[str]) -> typing.List[typing.List[str]]:
    """
    собрать список из списков [first_word, знак препинания, "", сгенерированные следующее слово]
    """
    rez = []
    for punctuation in punctuations:
        for count in (1, 2, 5, 20):
            rez.append([first_word, punctuation, "", get_next_words(count)])
    return rez


def wrong_generate_phrases_next_word(first_word: str, punctuations: typing.Iterable[str]) -> typing.List[str]:
    """get string like %karma_trigger%%punctuation%%next_words% without spaces"""
    precursors_lists = get_wrong_next_word_parts(first_word, punctuations)
    return ["".join(precursors_list) for precursors_list in precursors_lists]


def get_next_words(count_symbols: int = 10) -> str:
    return ''.join(choice(ascii_letters) for _ in range(count_symbols))


def get_message_with_text(text: str) -> types.Message:
    return types.Message(
        message_id=1,
        date=datetime.now(),
        text=text,
        chat=types.Chat(id=1, type="group"),
    )
