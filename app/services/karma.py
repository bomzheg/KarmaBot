import typing

from aiogram.utils.markdown import hbold
from app.models import Chat, User, UserKarma
from app.utils.exceptions import NotHaveNeighbours


async def get_karma_top(chat: Chat, user: User, limit: int = 15):
    text_list = ""
    user_ids = set()
    for i, (user_, karma) in enumerate(await chat.get_top_karma_list(limit), 1):
        text_list += f"\n{i} {user_.mention_no_link} {hbold(karma)}"
        user_ids.add(user_.id)
    if text_list == "":
        text = "Никто в чате не имеет кармы"
    else:
        text = "Список самых почётных пользователей чата:" + text_list
    try:
        prev_uk, user_uk, next_uk = await chat.get_neighbours(user)
    except NotHaveNeighbours:
        pass
    else:
        number_user_in_top = await user.get_number_in_top_karma(chat)
        if prev_uk.user.id not in user_ids:
            text += "\n..."
            text += f"\n{number_user_in_top - 1} {prev_uk.user.mention_no_link} {hbold(prev_uk.karma_round)}"
        if user_uk.user.id not in user_ids:
            text += f"\n{number_user_in_top} {user_uk.user.mention_no_link} {hbold(user_uk.karma_round)}"
        if next_uk.user.id not in user_ids:
            text += f"\n{number_user_in_top + 1} {next_uk.user.mention_no_link} {hbold(next_uk.karma_round)}"
    return text


async def get_me_chat_info(user: User, chat: Chat) -> typing.Tuple[UserKarma, int]:
    uk, _ = await UserKarma.get_or_create(chat=chat, user=user)
    number_in_top = await uk.number_in_top()
    return uk, number_in_top


async def get_me_info(user: User) -> typing.List[typing.Tuple[UserKarma, int]]:
    uks = await UserKarma.filter(user=user).prefetch_related("chat").all()
    return [(uk, await uk.number_in_top()) for uk in uks]
