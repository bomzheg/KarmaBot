import typing

from aiogram import types
from loguru import logger
from pyrogram.errors import UsernameNotOccupied
from tortoise.exceptions import MultipleObjectsReturned

from app.models import User
from app.services.user_getter import UserGetter
from app.utils.exceptions import UserWithoutUserIdError


def get_target_user(message: types.Message, can_be_same=False, can_be_bot=False) -> typing.Optional[types.user.User]:
    """
    Target user can be take from reply or by mention
    :param message:
    :param can_be_same:
    :param can_be_bot:
    :return:
    """

    author_user = message.from_user

    target_user = get_replied_user(message)
    if has_target_user(target_user, author_user, can_be_same, can_be_bot):
        return target_user

    target_user = get_mentioned_user(message)
    if has_target_user(target_user, author_user, can_be_same, can_be_bot):
        return target_user
    return None


def has_target_user(target_user: types.User, author_user: types.User, can_be_same, can_be_bot):
    """
    :return: True if target_user exist, not is author and not bot
    """
    if target_user is None:
        return False
    if not can_be_bot and target_user.is_bot:
        #   and not is_bot_username(target_user.username)
        # don't check is_bot_username because user can have username like @user_bot
        return False
    if not can_be_same and is_one_user(author_user, target_user):
        return False

    return True


def is_one_user(user_1: types.User, user_2: types.User):
    if all([
        user_1.id is not None,
        user_2.id is not None,
        user_1.id == user_2.id,
    ]):
        return True
    if all([
        user_1.username is not None,
        user_2.username is not None,
        user_1.username == user_2.username,
    ]):
        return True

    return False


def get_mentioned_user(message: types.Message) -> typing.Optional[types.User]:
    if not message.text:
        return None
    if not message.entities:
        return None
    for ent in message.entities:
        if ent.type == "text_mention":
            return ent.user
        elif ent.type == "mention":
            username = ent.get_text(message.text).lstrip("@")
            return types.User(username=username)
    return None


def get_replied_user(message: types.Message) -> typing.Optional[types.User]:
    if message.reply_to_message:
        return message.reply_to_message.from_user
    return None


def is_bot_username(username: str):
    """
    this function deprecated. user can use username like @alice_bot and it don't say that it is bot
    """
    return username is not None and username[-3:] == "bot"


async def get_db_user_by_tg_user(target: types.User) -> User:
    exception: Exception
    try:
        target_user = await User.get_or_create_from_tg_user(target)
    except MultipleObjectsReturned as e:
        logger.warning("Strange, multiple username? chek id={id}, username={username}",
                       id=target.id, username=target.username)
        exception = e
    # In target can be user with only username
    except UserWithoutUserIdError as e:
        exception = e
    else:
        return target_user

    try:
        async with UserGetter() as user_getter:
            tg_user = await user_getter.get_user_by_username(target.username)

        target_user = await User.get_or_create_from_tg_user(tg_user)
        # That username can be not valid
    except (UsernameNotOccupied, IndexError):
        raise exception
    return target_user
