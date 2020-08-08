import typing

from .common import plus_texts, minus_texts, punctuations, filter_check
from .fixtures import get_from_user, generate_phrases_next_word, get_message_with_reply, \
    get_message_with_text_mention, get_message_with_mention, get_next_word_parts


def test_reply():
    user = get_from_user(321, "Kripke")
    for text in [*plus_texts, *minus_texts]:
        for phrase in generate_phrases_next_word(text, punctuations):
            check_plus_reply(user, phrase)


def check_plus_reply(user: dict, text_with_plus_trigger: str):
    filter_rez = filter_check(get_message_with_reply(user, user, text_with_plus_trigger))
    assert filter_rez == {}


def test_plus_mention():
    user = get_from_user(321, "Kripke")

    for text in [*plus_texts, *minus_texts]:
        for precursors_list in get_next_word_parts(text, punctuations):
            check_plus_mention(user, precursors_list)


def check_plus_mention(user: dict, text_precursors: typing.List[str]):
    filter_rez = filter_check(get_message_with_mention(user, user, text_precursors))
    assert filter_rez == {}


def test_plus_text_mention():
    user = get_from_user(321, first_name="Barry")

    for text in [*plus_texts, *minus_texts]:
        for precursors_list in get_next_word_parts(text, punctuations):
            check_plus_text_mention(user, precursors_list)


def check_plus_text_mention(user: dict, text_precursors: typing.List[str]):
    filter_rez = filter_check(get_message_with_text_mention(user, user, text_precursors))
    assert filter_rez == {}
