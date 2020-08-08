import typing

from .common import PLUS_TRIGGERS, MINUS, punctuations, filter_check
from .fixtures import (get_from_user, wrong_generate_phrases_next_word, get_message_with_reply,
                       get_message_with_text_mention, generate_phrases_next_word, get_wrong_next_word_parts)


def test_plus_reply():
    target_user = get_from_user(666, "Sheldon")
    author_user = get_from_user(13, "Leonard")
    for text in PLUS_TRIGGERS:
        for phrase in wrong_generate_phrases_next_word(text, punctuations):
            check_plus_reply(author_user, target_user, phrase)


def check_plus_reply(author_user: dict, target_user: dict, text_with_plus_trigger: str):
    filter_rez = filter_check(get_message_with_reply(author_user, target_user, text_with_plus_trigger))
    assert filter_rez == {}


def test_minus_reply():
    target_user = get_from_user(99, "Howard")
    author_user = get_from_user(36, "Rajesh")

    for text in MINUS:
        for phrase in generate_phrases_next_word(text, punctuations):
            check_plus_reply(author_user, target_user, phrase)
        for phrase in wrong_generate_phrases_next_word(text, punctuations):
            check_minus_reply(author_user, target_user, phrase)


def check_minus_reply(author_user: dict, target_user: dict, text_with_minus_trigger: str):
    filter_rez = filter_check(get_message_with_reply(author_user, target_user, text_with_minus_trigger))
    assert filter_rez == {}


def test_plus_text_mention():
    target_user = get_from_user(37, first_name="Leslie")
    author_user = get_from_user(50, "Stuart")

    for text in PLUS_TRIGGERS:
        for precursors_list in get_wrong_next_word_parts(text, punctuations):
            check_plus_text_mention(author_user, target_user, precursors_list)


def check_plus_text_mention(author_user: dict, target_user: dict, text_precursors: typing.List[str]):
    filter_rez = filter_check(get_message_with_text_mention(author_user, target_user, text_precursors))
    assert filter_rez == {}
