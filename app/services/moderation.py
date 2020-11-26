import typing
from datetime import timedelta

from aiogram import Bot
from aiogram.utils.exceptions import BadRequest
from loguru import logger

from app import config
from app.models import ModeratorEvent, User, Chat
from app.models.common import TypeRestriction
from app.utils.exceptions import CantRestrict
from app.utils.timedelta_functions import parse_timedelta_from_text, format_timedelta


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
    if duration < config.FOREVER_DURATION:
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
        # restrict in telegram
        await config.action_for_restrict[type_restriction](
            bot,
            chat_id=chat.chat_id,
            user_id=target.tg_id,
            until_date=duration,
        )
    except BadRequest as e:
        raise CantRestrict(
            text=e.text, user_id=target.tg_id, chat_id=chat.chat_id,
            reason=comment, type_event=type_restriction.name
        )
    else:
        moderator_event = await ModeratorEvent.save_new_action(
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
        return moderator_event


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
        duration = config.DEFAULT_DURATION
    return duration, comment


def check_need_auto_restrict(karma: float):
    return all([
        config.ENABLE_AUTO_RESTRICT_ON_NEGATIVE_KARMA,
        karma <= config.NEGATIVE_KARMA_TO_RESTRICT,
    ])


async def user_has_now_ro(user: User, chat: Chat, bot: Bot):
    chat_member = await bot.get_chat_member(chat_id=chat.chat_id, user_id=user.tg_id)
    return chat_member.can_send_messages is False


async def auto_restrict(target: User, chat: Chat, bot: Bot, using_db=None) -> typing.Tuple[int, ModeratorEvent]:
    """
    return count auto restrict
    """
    bot_user = await User.get_or_create_from_tg_user(await bot.me)

    count_auto_restrict = await ModeratorEvent.filter(
        moderator=bot_user, user=target, chat=chat,
        type_restriction__in=(TypeRestriction.karmic_ro.name, TypeRestriction.karmic_ban.name),
    ).count()
    logger.info(
        "auto restrict user {user} in chat {chat} for to negative karma. "
        "previous restrict count: {count}",
        user=target.tg_id,
        chat=chat.chat_id,
        count=count_auto_restrict,
    )

    if it_was_last_one_auto_restrict(count_auto_restrict):
        current_restriction = config.RESTRICTIONS_PLAN[-1]
    else:
        current_restriction = config.RESTRICTIONS_PLAN[count_auto_restrict]

    moderator_event = await restrict(
        bot=bot,
        chat=chat,
        target=target,
        admin=bot_user,
        duration=current_restriction.duration,
        comment=config.COMMENT_AUTO_RESTRICT,
        type_restriction=current_restriction.type_restriction,
        using_db=using_db,
    )
    return count_auto_restrict + 1, moderator_event


def it_was_last_one_auto_restrict(count_auto_restrict: int) -> bool:
    return count_auto_restrict >= len(config.RESTRICTIONS_PLAN)
