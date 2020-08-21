import typing
from random import choice
from string import ascii_letters

from aiogram import types


def get_parts() -> typing.List[typing.List[str]]:
    """
    собрать список из списков [сгенерированное слово, "", сгенерированное слово]
    """
    rez = []
    for count_first in (0, 1, 2, 20):
        for count_last in (0, 1, 2, 20):
            rez.append([get_words(count_first), "", get_words(count_last)])
    return rez


def get_words(count_symbols: int = 10) -> str:
    return ''.join(choice(ascii_letters) for _ in range(count_symbols))


def get_message_with_reply(author_user: dict, target_user: dict, text: str) -> types.Message:
    return types.Message(**{
        'from': author_user,
        'text': text,
        'reply_to_message': get_reply_message(target_user)
    })


def get_message_with_mention(author_user: dict, target_user: dict, text_precursors: typing.List[str]) -> types.Message:
    username = get_user_username(target_user)
    text_precursors[1] = username
    msg_text = " ".join(text_precursors)
    start_entity_pos = len(text_precursors[0]) + 1  # добавляем длину пробела
    return types.Message(**{
        'from': author_user,
        'text': msg_text,
        'entities': [
            get_entity_mention(start_entity_pos, len(username)),
        ]
    })


def get_entity_mention(offset, length):
    return {
        "offset": offset,
        "length": length,
        "type": "mention"
    }


def get_message_with_text_mention(
        author_user: dict,
        target_user: dict,
        text_precursors: typing.List[str]
) -> types.Message:
    first_name = target_user['first_name']
    text_precursors[1] = first_name
    msg_text = " ".join(text_precursors)
    start_entity_pos = len(text_precursors[0]) + 1  # добавляем длину пробела
    return types.Message(**{
        'from': author_user,
        'text': msg_text,
        'entities': [
            get_entity_text_mention(start_entity_pos, target_user)
        ]
    })


def get_entity_text_mention(offset, user: dict):
    return {
        "offset": offset,
        "length": len(user["first_name"]),
        "type": "text_mention",
        "user": user
    }


def get_user_username(user: dict) -> str:
    return f"@{user['username']}"


def get_reply_message(user_dict):
    return types.Message(**{
        'from': user_dict
    })


def get_from_user(id_=777, username=None, first_name=None):
    return {
        'id': id_,
        'username': username,
        'first_name': first_name
    }
