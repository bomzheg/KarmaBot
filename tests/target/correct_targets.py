from aiogram import types

from .common import filter_check, CONF_CANT_BE_SAME
from .fixtures import (get_from_user, get_message_with_reply,
                       get_message_with_text_mention, get_message_with_mention, get_parts)


def test_reply_target():
    author_user = get_from_user(13, "Leonard")
    target_user = get_from_user(666, "Sheldon")
    msg = get_message_with_reply(author_user, target_user, "Sarcasm!!!")
    check_target(target_user, msg)


def test_mention_target():
    author_user = get_from_user(36, "Rajesh")
    target_user = get_from_user(99, "Howard")
    for phrase in get_parts():
        msg = get_message_with_mention(author_user, target_user, phrase)
        check_target(target_user, msg)


def test_text_mention_target():
    target_user = get_from_user(69, "Bernadette")
    author_user = get_from_user(53, "Amy")

    for phrase in get_parts():
        msg = get_message_with_text_mention(author_user, target_user, phrase)
        check_target(target_user, msg)


def check_target(target_user: dict, msg: types.Message):
    filter_rez = filter_check(msg, CONF_CANT_BE_SAME)
    assert filter_rez != {}, f"msg text {{{msg.text}}}"
    target_user = types.User(**target_user)
    founded_user = filter_rez["target"]
    if founded_user.id is None:
        assert founded_user.username == target_user.username, f"msg text {{{msg.text}}} user: {{{target_user}}}"
    else:
        assert founded_user == target_user, f"msg text {{{msg.text}}} user: {{{target_user}}}"
