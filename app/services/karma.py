import typing

from aiogram.utils.markdown import hbold

from app.infrastructure.database.models import Chat, User, UserKarma
from app.utils.exceptions import NotHaveNeighbours


async def get_top(chat: Chat, user: User, limit: int = 15):
    top_karmas = await chat.get_top_karma_list(limit)
    text_list = format_output([(i, user, karma) for i, (user, karma) in enumerate(top_karmas, 1)])
    text = add_caption(text_list)
    try:
        prev_uk, user_uk, next_uk = await chat.get_neighbours(user)
    except NotHaveNeighbours:
        return text

    user_ids = get_top_ids(top_karmas)
    number_user_in_top = await user.get_number_in_top_karma(chat)
    neighbours_karmas = []
    if prev_uk.user.id not in user_ids:
        text = add_separator(text)
        neighbours_karmas.append((number_user_in_top - 1, prev_uk.user, prev_uk.karma_round))
    if user_uk.user.id not in user_ids:
        neighbours_karmas.append((number_user_in_top, user_uk.user, user_uk.karma_round))
    if next_uk.user.id not in user_ids:
        neighbours_karmas.append((number_user_in_top + 1, next_uk.user, next_uk.karma_round))
    additional_users = format_output(neighbours_karmas)
    return text + "\n" + additional_users


def format_output(list_karmas: typing.List[typing.Tuple[int, User, float]]) -> str:
    return "\n".join(
        [f"{i} {user.mention_no_link} {hbold(karma)}" for i, user, karma in list_karmas]
    )


def add_caption(text_list: str) -> str:
    if text_list == "":
        text = "Никто в чате не имеет кармы"
    else:
        text = "Список самых почётных пользователей чата:\n" + text_list
    return text


def add_separator(text: str) -> str:
    return text + "\n..."


def get_top_ids(list_karmas: typing.List[typing.Tuple[User, float]]) -> typing.Set[int]:
    return {user.id for user, _ in list_karmas}


async def get_me_chat_info(user: User, chat: Chat) -> typing.Tuple[UserKarma, int]:
    uk, _ = await UserKarma.get_or_create(chat=chat, user=user)
    number_in_top = await uk.number_in_top()
    return uk, number_in_top


async def get_me_info(user: User) -> typing.List[typing.Tuple[UserKarma, int]]:
    uks = await UserKarma.filter(user=user).prefetch_related("chat").all()
    return [(uk, await uk.number_in_top()) for uk in uks]
