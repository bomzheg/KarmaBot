import typing
from datetime import timedelta

from aiogram import types
from aiogram.utils.exceptions import BadRequest
from loguru import logger

from app.models import ModeratorEvent, User, Chat
from app.utils.exceptions import CantRestrict
from app.utils.timedelta_functions import parse_timedelta_from_text, format_timedelta

DEFAULT_DURATION = timedelta(hours=1)
FOREVER_DURATION = timedelta(days=366)


async def warn_user(moderator: User, target_user: User, chat: Chat, comment: str):
    return await ModeratorEvent.save_new_action(
        moderator=moderator,
        user=target_user,
        chat_id=chat.chat_id,
        type_restriction="warn",
        comment=comment
    )


async def ban_user(chat: types.Chat, target: User, admin: User, duration: timedelta, comment: str):
    type_restriction = 'ban'
    try:
        await chat.kick(target.tg_id, until_date=duration)
    except BadRequest as e:
        logger.error("Failed to kick chat member: {error!r}", error=e)
        raise CantRestrict(
            text=e.text, user_id=target.tg_id, chat_id=chat.id, reason=comment, type_event=type_restriction
        )
    else:
        await ModeratorEvent.save_new_action(
            moderator=admin,
            user=target,
            chat_id=chat.id,
            type_restriction=type_restriction,
            duration=duration,
            comment=comment,
        )
        logger.info(
            "User {user} kicked by {admin} for {duration}",
            user=target.tg_id,
            admin=admin.tg_id,
            duration=duration,
        )
        text = "Пользователь {user} попал в бан этого чата.".format(user=target.mention_link)
        if duration < FOREVER_DURATION:
            text += " Он сможет вернуться через {duration}".format(duration=format_timedelta(duration))
        return text


async def ro_user(chat: types.Chat, target: User, admin: User, duration: timedelta, comment: str):
    type_restriction = 'ro'
    try:
        await chat.restrict(target.tg_id, can_send_messages=False, until_date=duration)
    except BadRequest as e:
        logger.error("Failed to restrict chat member: {error!r}", error=e)
        raise CantRestrict(
            text=e.text, user_id=target.tg_id, chat_id=chat.id, reason=comment, type_event=type_restriction
        )
    else:
        await ModeratorEvent.save_new_action(
            moderator=admin,
            user=target,
            chat_id=chat.id,
            type_restriction=type_restriction,
            duration=duration,
            comment=comment,
        )
        logger.info(
            "User {user} restricted by {admin} for {duration}",
            user=target.tg_id,
            admin=admin.tg_id,
            duration=duration,
        )
        return "Пользователь {user} сможет <b>только читать</b> сообщения на протяжении {duration}".format(
            user=target.mention_link,
            duration=format_timedelta(duration),
        )


def get_moderator_message_args(text: str) -> typing.Tuple[str, str]:
    _, *args = text.split(maxsplit=2)  # in text: command_duration_comments like: "!ro 13d don't flood"
    if not args:
        return "", ""
    duration_text = args[0]
    if len(args) == 1:
        return duration_text, ""
    return duration_text, " ".join(args[1:])


def get_duration(text: str):
    duration_text, comment = get_moderator_message_args(text)
    if duration_text:
        duration = parse_timedelta_from_text(duration_text)
    else:
        duration = DEFAULT_DURATION
    return duration, comment
