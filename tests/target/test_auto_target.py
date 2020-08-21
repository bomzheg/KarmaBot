import typing

from .common import filter_check
from .fixtures import get_from_user, get_message_with_reply, \
    get_message_with_text_mention, get_message_with_mention, get_parts

CONF = dict(can_be_same=False)


def test_auto_reply():
    user = get_from_user(321, "Kripke")
    for phrase in get_parts():
        check_auto_reply(user, " ".join(phrase))


def check_auto_reply(user: dict, text_with_plus_trigger: str):
    msg = get_message_with_reply(user, user, text_with_plus_trigger)
    filter_rez = filter_check(msg, CONF)
    assert filter_rez == {}, f"msg text {{{msg.text}}} user: {{{user}}}"


def test_auto_mention():
    user = get_from_user(321, "Kripke")

    for phrase in get_parts():
        check_auto_mention(user, phrase)


def check_auto_mention(user: dict, text_precursors: typing.List[str]):
    msg = get_message_with_mention(user, user, text_precursors)
    filter_rez = filter_check(msg, CONF)
    assert filter_rez == {}, f"msg text {{{msg.text}}} user: {{{user}}}"


def test_auto_text_mention():
    user = get_from_user(321, first_name="Barry")

    for phrase in get_parts():
        check_auto_text_mention(user, phrase)


def check_auto_text_mention(user: dict, text_precursors: typing.List[str]):
    msg = get_message_with_text_mention(user, user, text_precursors)
    filter_rez = filter_check(msg, CONF)
    assert filter_rez == {}, f"msg text {{{msg.text}}} user: {{{user}}}"
