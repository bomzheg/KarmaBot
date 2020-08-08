import typing
from random import choice, randint
from string import ascii_letters

from aiogram import types

SPACES = (" ", "\t", "\n", "\r")


def get_next_word_parts(first_word: str, punctuations: typing.Iterable[str]) -> typing.List[typing.List[str]]:
    rez = []
    for punctuation in punctuations:
        for space in SPACES:
            for count in (0, 1, 2, 5, 20):
                rez.append([first_word, punctuation, space, get_next_words(count)])
    return rez


def generate_phrases_next_word(first_word: str, punctuations: typing.Iterable[str]) -> typing.List[str]:
    precursors_lists = get_next_word_parts(first_word, punctuations)
    return ["".join(precursors_list) for precursors_list in precursors_lists]


def get_wrong_next_word_parts(first_word: str, punctuations: typing.Iterable[str]) -> typing.List[typing.List[str]]:
    rez = []
    for punctuation in punctuations:
        for count in (1, 2, 5, 20):
            rez.append([first_word, punctuation, "", get_next_words(count)])
    return rez


def wrong_generate_phrases_next_word(first_word: str, punctuations: typing.Iterable[str]) -> typing.List[str]:
    precursors_lists = get_wrong_next_word_parts(first_word, punctuations)
    return ["".join(precursors_list) for precursors_list in precursors_lists]


def get_next_words(count_symbols: int = 10) -> str:
    return ''.join(choice(ascii_letters) for _ in range(count_symbols))


def get_message_with_reply(author_user: dict, target_user: dict, text: str) -> types.Message:
    return types.Message(**{
        'from': author_user,
        'text': text,
        'reply_to_message': get_reply_message(target_user)
    })


def get_message_with_mention(author_user: dict, target_user: dict, text_precursors: typing.List[str]) -> types.Message:
    username = get_user_username(target_user)
    offset = randint(0, len(text_precursors[-1]))
    text_precursors[-1] = text_precursors[-1][:offset] + f" {username} " + text_precursors[-1][offset:]
    msg_text = "".join(text_precursors)
    start_entity_pos = sum((len(part) for part in text_precursors[:-1])) + offset
    if text_precursors[0] == "👍":
        start_entity_pos += 1  # ебучий костыль, задрало меня считать в разных кодировках
    return types.Message(**{
        'from': author_user,
        'text': msg_text,
        'entities': [
            get_entity_mention(start_entity_pos + 1, len(username)),
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
    offset = randint(0, len(text_precursors[-1]))
    text_precursors[-1] = text_precursors[-1][:offset] + f"{first_name}" + text_precursors[-1][offset:]
    msg_text = "".join(text_precursors)
    start_entity_pos = sum((len(part) for part in text_precursors[:-1])) + offset
    if text_precursors[0] == "👍":
        start_entity_pos += 1  # ебучий костыль, задрало меня считать в разных кодировках
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
