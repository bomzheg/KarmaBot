import typing
from contextlib import suppress

from aiogram import types
from pyrogram.errors import UsernameNotOccupied
from tortoise.exceptions import MultipleObjectsReturned

from app.models import dto
from app.models.config import TgClientConfig
from app.models.db import User
from app.services.user_getter import UserGetter
from app.utils.exceptions import UserWithoutUserIdError
from app.utils.log import Logger


logger = Logger(__name__)


def get_target_user(message: types.Message, can_be_same=False, can_be_bot=False) -> typing.Optional[dto.TargetUser]:
    """
    Target user can be take from reply or by mention
    :param message:
    :param can_be_same:
    :param can_be_bot:
    :return:
    """
    author_user = dto.TargetUser.from_aiogram(message.from_user)

    target_user = get_replied_user(message)
    if has_target_user(target_user, author_user, can_be_same, can_be_bot):
        return target_user

    target_user = get_mentioned_user(message)
    if has_target_user(target_user, author_user, can_be_same, can_be_bot):
        return target_user

    target_user = get_id_user(message)
    if has_target_user(target_user, author_user, can_be_same, can_be_bot):
        return target_user

    return None


def has_target_user(target_user: dto.TargetUser, author_user: dto.TargetUser, can_be_same, can_be_bot):
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


def is_one_user(user_1: dto.TargetUser, user_2: dto.TargetUser):
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


def get_mentioned_user(message: types.Message) -> typing.Optional[dto.TargetUser]:
    possible_mentioned_text = message.text or message.caption
    if not possible_mentioned_text:
        return None
    entities = message.entities or message.caption_entities
    if not entities:
        return None
    for ent in entities:
        if ent.type == "text_mention":
            return dto.TargetUser.from_aiogram(ent.user)
        elif ent.type == "mention":
            username = ent.extract_from(possible_mentioned_text).lstrip("@")
            return dto.TargetUser(username=username)
    return None


def get_replied_user(message: types.Message) -> typing.Optional[dto.TargetUser]:
    if message.reply_to_message:
        return dto.TargetUser.from_aiogram(message.reply_to_message.from_user)
    return None


def get_id_user(message: types.Message) -> dto.TargetUser | None:
    text = message.text or message.caption or ""
    for word in text.lower().split():
        if word.startswith("id"):
            with suppress(ValueError):
                user_id = int(word.removeprefix("id"))
                return dto.TargetUser(id=user_id)
    return None


def is_bot_username(username: str):
    """
    this function deprecated. user can use username like @alice_bot and it don't say that it is bot
    """
    return username is not None and username[-3:] == "bot"


async def get_db_user_by_tg_user(target: dto.TargetUser, tg_client_config: TgClientConfig) -> User:
    exception: Exception
    try:
        target_user = await User.get_or_create_from_tg_user(target)
    except MultipleObjectsReturned as e:
        logger.warning("Strange, multiple username? check id={id}, username={username}",
                       id=target.id, username=target.username)
        exception = e
    # In target can be user with only username
    except UserWithoutUserIdError as e:
        exception = e
    else:
        return target_user

    try:
        async with UserGetter(tg_client_config) as user_getter:
            tg_user = await user_getter.get_user_by_username(target.username)

        target_user = await User.get_or_create_from_tg_user(tg_user)
        # That username can be not valid
    except (UsernameNotOccupied, IndexError):
        raise exception
    return target_user
