import pytest

from .common import INF, SPACES, filter_check, minus_texts, plus_texts, punctuations
from .fixtures import generate_phrases_next_word, get_message_with_text


@pytest.mark.parametrize("text", plus_texts)
def test_correct_plus(text: str):
    for phrase in generate_phrases_next_word(text, punctuations, SPACES):
        check_plus(phrase)


def check_plus(text_with_plus_trigger: str):
    msg = get_message_with_text(text_with_plus_trigger)
    filter_rez = filter_check(msg)
    assert filter_rez["karma"]["karma_change"] == INF, str(msg)


@pytest.mark.parametrize("text", minus_texts)
def test_correct_minus(text: str):
    for phrase in generate_phrases_next_word(text, punctuations, SPACES):
        check_minus_reply(phrase)


def check_minus_reply(text_with_minus_trigger: str):
    msg = get_message_with_text(text_with_minus_trigger)
    filter_rez = filter_check(msg)
    assert filter_rez["karma"]["karma_change"] == -INF, str(msg)
