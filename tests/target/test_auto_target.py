from aiogram import types

from .common import filter_check, CONF_CAN_BE_SAME, CONF_CANT_BE_SAME
from .fixtures import (get_from_user, get_message_with_reply,
                       get_message_with_text_mention, get_message_with_mention, get_parts)


def test_auto_reply():
    user = get_from_user(321, "Kripke")
    for phrase in get_parts():
        msg = get_message_with_reply(user, user, " ".join(phrase))
        check_msg_auto_target(user, msg)


def test_auto_mention():
    user = get_from_user(321, "Kripke")

    for phrase in get_parts():
        msg = get_message_with_mention(user, user, phrase)
        check_msg_auto_target(user, msg)


def test_auto_text_mention():
    user = get_from_user(321, first_name="Barry")

    for phrase in get_parts():
        msg = get_message_with_text_mention(user, user, phrase)
        check_msg_auto_target(user, msg)


def check_msg_auto_target(user: dict, msg: types.Message):
    filter_rez = filter_check(msg, CONF_CANT_BE_SAME)
    assert filter_rez == {}, f"msg text {{{msg.text}}} user: {{{user}}}"
    filter_rez = filter_check(msg, CONF_CAN_BE_SAME)
    assert filter_rez != {}, f"msg text {{{msg.text}}} user: {{{user}}}"
    target_user = types.User(**user)
    founded_user = filter_rez["target"]
    if founded_user.id is None:
        assert founded_user.username == target_user.username, f"msg text {{{msg.text}}} user: {{{user}}}"
    else:
        assert founded_user == target_user, f"msg text {{{msg.text}}} user: {{{user}}}"
