import pytest
from aiogram import types

from .common import filter_check, CONF_CAN_BE_SAME, CONF_CANT_BE_SAME
from .fixtures import (get_from_user, get_message_with_reply,
                       get_message_with_text_mention, get_message_with_mention, get_parts)


@pytest.mark.parametrize("phrase", get_parts())
def test_auto_reply(phrase: list[str]):
    user = get_from_user(321, "Kripke")
    msg = get_message_with_reply(user, user, " ".join(phrase))
    check_msg_auto_target(user, msg)


@pytest.mark.parametrize("phrase", get_parts())
def test_auto_mention(phrase: list[str]):
    user = get_from_user(321, "Kripke")
    msg = get_message_with_mention(user, user, phrase)
    check_msg_auto_target(user, msg)


@pytest.mark.parametrize("phrase", get_parts())
def test_auto_text_mention(phrase: list[str]):
    user = get_from_user(321, first_name="Barry")
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
        assert are_users_equals(founded_user, target_user), f"msg text {{{msg.text}}} user: {{{user}}}"


def are_users_equals(expected: types.User, actual: types.User) -> bool:
    return all([
        expected.id == actual.id,
        expected.is_bot == actual.is_bot,
        expected.username == actual.username,
        expected.first_name == actual.first_name,
        expected.last_name == actual.last_name,
    ])
