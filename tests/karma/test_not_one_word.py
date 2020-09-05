from .common import PLUS_TRIGGERS, MINUS_TRIGGERS, punctuations, filter_check
from .fixtures import (wrong_generate_phrases_next_word, get_message_with_text,
                       generate_phrases_next_word)


def test_plus():
    """проверка что триггер не находится, если после триггера и знака препинания нет пробельного символа"""
    for text in PLUS_TRIGGERS:
        for phrase in wrong_generate_phrases_next_word(text, punctuations):
            check_plus(phrase)


def check_plus(text_with_plus_trigger: str):
    msg = get_message_with_text(text_with_plus_trigger)
    filter_rez = filter_check(msg)
    assert filter_rez == {}, str(msg)


def test_minus():
    """проверка что триггер не находится, если кроме триггера на первой строке сообщения есть посторонние символы"""
    spaces_without_new_lines = (" ", "\t")
    for text in MINUS_TRIGGERS:
        # next words on the same line. in message with minus trigger can't not
        for phrase in generate_phrases_next_word(text, punctuations, spaces_without_new_lines):
            check_plus(phrase)

        for phrase in wrong_generate_phrases_next_word(text, punctuations):
            check_minus(phrase)


def check_minus(text_with_minus_trigger: str):
    msg = get_message_with_text(text_with_minus_trigger)
    filter_rez = filter_check(msg)
    assert filter_rez == {}, str(msg)
