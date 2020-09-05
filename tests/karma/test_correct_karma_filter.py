from .common import plus_texts, minus_texts, punctuations, filter_check, SPACES, INF
from .fixtures import generate_phrases_next_word, get_message_with_text


def test_correct_plus():
    for text in plus_texts:
        for phrase in generate_phrases_next_word(text, punctuations, SPACES):
            check_plus(phrase)


def check_plus(text_with_plus_trigger: str):
    msg = get_message_with_text(text_with_plus_trigger)
    filter_rez = filter_check(msg)
    assert filter_rez['karma']['karma_change'] == INF, str(msg)


def test_correct_minus():
    for text in minus_texts:
        for phrase in generate_phrases_next_word(text, ("",), ("\n",)):
            check_minus_reply(phrase)


def check_minus_reply(text_with_minus_trigger: str):
    msg = get_message_with_text(text_with_minus_trigger)
    filter_rez = filter_check(msg)
    assert filter_rez['karma']['karma_change'] == -INF, str(msg)
