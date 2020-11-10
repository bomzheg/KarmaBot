import typing
from datetime import timedelta
from enum import Enum
from functools import partial

from aiogram import Bot
from aiogram.utils.exceptions import BadRequest
from loguru import logger

from app import config
from app.models import ModeratorEvent, User, Chat
from app.utils.exceptions import CantRestrict
from app.utils.timedelta_functions import parse_timedelta_from_text, format_timedelta

DEFAULT_DURATION = timedelta(hours=1)
FOREVER_DURATION = timedelta(days=366)


class TypeRestriction(Enum):
    ro = "ro"
    ban = "ban"
    warn = "warn"


action_for_restrict = {
    TypeRestriction.ban: Bot.kick_chat_member,
    TypeRestriction.ro: partial(Bot.restrict_chat_member, can_send_messages=False),
}


async def warn_user(moderator: User, target_user: User, chat: Chat, comment: str):
    return await ModeratorEvent.save_new_action(
        moderator=moderator,
        user=target_user,
        chat=chat,
        type_restriction=TypeRestriction.warn.name,
        comment=comment,
    )


async def ban_user(chat: Chat, target: User, admin: User, duration: timedelta, comment: str, bot: Bot):
    await restrict(
        bot=bot,
        chat=chat,
        target=target,
        admin=admin,
        duration=duration,
        comment=comment,
        type_restriction=TypeRestriction.ban
    )
    text = "Пользователь {user} попал в бан этого чата.".format(user=target.mention_link)
    if duration < FOREVER_DURATION:
        text += " Он сможет вернуться через {duration}".format(duration=format_timedelta(duration))
    return text


async def ro_user(chat: Chat, target: User, admin: User, duration: timedelta, comment: str, bot: Bot):
    await restrict(
        bot=bot,
        chat=chat,
        target=target,
        admin=admin,
        duration=duration,
        comment=comment,
        type_restriction=TypeRestriction.ro,
    )
    return "Пользователь {user} сможет <b>только читать</b> сообщения на протяжении {duration}".format(
        user=target.mention_link,
        duration=format_timedelta(duration),
    )


async def restrict(
        bot: Bot,
        chat: Chat,
        target: User,
        admin: User,
        duration: timedelta,
        comment: str,
        type_restriction: TypeRestriction,
        using_db=None
):
    try:
        await action_for_restrict[type_restriction](
            bot,
            chat_id=chat.chat_id,
            user_id=target.tg_id,
            until_date=duration,
        )
    except BadRequest as e:
        raise CantRestrict(
            text=e.text, user_id=target.tg_id, chat_id=chat.chat_id, reason=comment, type_event=type_restriction.name
        )
    else:
        await ModeratorEvent.save_new_action(
            moderator=admin,
            user=target,
            chat=chat,
            type_restriction=type_restriction.name,
            duration=duration,
            comment=comment,
            using_db=using_db,
        )
        logger.info(
            "User {user} restricted ({type_restriction}) by {admin} for {duration} in chat {chat}",
            user=target.tg_id,
            type_restriction=type_restriction.name,
            admin=admin.tg_id,
            duration=duration,
            chat=chat.chat_id,
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


async def auto_restrict(target: User, chat: Chat, bot: Bot, using_db=None) -> TypeRestriction:
    bot_user = await User.get_or_create_from_tg_user(await bot.me)

    moderator_events = await ModeratorEvent.filter(
        moderator=bot_user, user=target, chat=chat, comment=config.COMMENT_AUTO_RESTRICT
    ).all()
    logger.info(
        "auto restrict user {user} in chat {chat} for to negative karma. previous restrict for the same: {events}",
        user=target.tg_id,
        chat=chat.chat_id,
        events=moderator_events,
    )

    if not moderator_events:
        type_restriction = TypeRestriction.ro
    else:
        type_restriction = TypeRestriction.ban

    await restrict(
        bot=bot,
        chat=chat,
        target=target,
        admin=bot_user,
        duration=config.DURATION_AUTO_RESTRICT,
        comment=config.COMMENT_AUTO_RESTRICT,
        type_restriction=type_restriction,
        using_db=using_db,
    )
    return type_restriction
