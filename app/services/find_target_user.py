from contextlib import suppress

from aiogram import types
from tortoise.exceptions import MultipleObjectsReturned

from app.infrastructure.database.models import User
from app.infrastructure.database.repo.user import UserRepo
from app.models import dto
from app.services.user_getter import UserGetter
from app.utils.exceptions import UserWithoutUserIdError
from app.utils.log import Logger

logger = Logger(__name__)


def get_target_user(
    message: types.Message, can_be_same=False, can_be_bot=False
) -> dto.TargetUser | None:
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


def has_target_user(
    target_user: dto.TargetUser,
    author_user: dto.TargetUser,
    can_be_same: bool,
    can_be_bot: bool,
) -> bool:
    """
    :return: True if target_user exist, not is author and not bot
    """
    if target_user is None:
        return False
    if not can_be_bot and target_user.is_bot:
        return False
    if not can_be_same and is_one_user(author_user, target_user):
        return False

    return True


def is_one_user(user_1: dto.TargetUser | None, user_2: dto.TargetUser | None) -> bool:
    if all(
        [
            user_1.id is not None,
            user_2.id is not None,
            user_1.id == user_2.id,
        ]
    ):
        return True
    if all(
        [
            user_1.username is not None,
            user_2.username is not None,
            user_1.username == user_2.username,
        ]
    ):
        return True

    return False


def get_mentioned_user(message: types.Message) -> dto.TargetUser | None:
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


def get_replied_user(message: types.Message) -> dto.TargetUser | None:
    if message.reply_to_message and not message.reply_to_message.forum_topic_created:
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


async def get_db_user_by_tg_user(
    target: dto.TargetUser, user_getter: UserGetter, user_repo: UserRepo
) -> User:
    try:
        return await user_repo.get_or_create_from_tg_user(target)
    except MultipleObjectsReturned:
        logger.error(
            "Found multiple users with the same username: id={id}, username={username}",
            id=target.id,
            username=target.username,
        )
    except UserWithoutUserIdError:
        logger.debug(
            "User with username={username} not found in database",
            username=target.username,
        )

    tg_user = await user_getter.get_user_by_username(target.username)
    target_user = await user_repo.get_or_create_from_tg_user(tg_user)

    return target_user
