import typing
from contextlib import suppress
from datetime import timedelta

from aiogram import types
from aiogram.dispatcher.filters.builtin import Command
from aiogram.utils.exceptions import BadRequest, Unauthorized, MessageCantBeDeleted, MessageToDeleteNotFound
from aiogram.utils.markdown import hide_link, quote_html
from loguru import logger

from app.misc import dp, bot
from app.utils.timedelta_functions import parse_timedelta_from_text, format_timedelta
from app.utils.exceptions import TimedeltaParseError
from app.models import ModeratorEvent, Chat, User
from app.services.user_info import get_user_info
FOREVER_DURATION = timedelta(days=366)
DEFAULT_DURATION = timedelta(hours=1)


async def report_filter(message: types.Message):
    if not types.ChatType.is_group_or_super_group(message):
        return False
    if not message.reply_to_message:
        return False
    if await Command(commands=['report', 'admin'], prefixes='/!@').check(message):
        return True
    return False


@dp.message_handler(report_filter)
@dp.throttled(rate=5)
async def report(message: types.Message):
    logger.info("user {user} report for message {message}", user=message.from_user.id, message=message.message_id)
    answer_template = "Спасибо за сообщение. Мы обязательно разберёмся. "
    admins_mention = await get_mentions_admins(message.chat)
    await message.reply(answer_template + admins_mention + " ")


async def get_mentions_admins(chat: types.Chat):
    admins = await chat.get_administrators()
    admins_mention = ""
    for admin in admins:
        logger.debug(admin.as_json())
        if admin.user.is_bot:
            continue
        if need_notify_admin(admin):
            admins_mention += hide_link(admin.user.url)
    return admins_mention


def need_notify_admin(admin: types.ChatMember):
    return admin.can_delete_messages or admin.can_restrict_members or admin.status == types.ChatMemberStatus.CREATOR


def get_moderator_message_args(text: str) -> typing.Tuple[str, str]:
    _, *args = text.split(maxsplit=2)  # in text: command_duration_comments
    if not args:
        return "", ""
    duration_text = args[0]
    if len(args) == 1:
        return duration_text, ""
    return duration_text, " ".join(args[1:])


@dp.message_handler(
    commands=["ro", "mute"],
    commands_prefix="!",
    is_reply=True,
    user_can_restrict_members=True,
    bot_can_restrict_members=True,
)
async def cmd_ro(message: types.Message, chat: Chat):
    duration_text, comment = get_moderator_message_args(message.text)
    if duration_text:
        try:
            duration = parse_timedelta_from_text(duration_text)
        except TimedeltaParseError as e:
            return await message.reply(f"Не могу распознать время. {quote_html(e.text)}")
    else:
        duration = DEFAULT_DURATION

    try:
        await message.chat.restrict(
            message.reply_to_message.from_user.id, can_send_messages=False, until_date=duration
        )
        logger.info(
            "User {user} restricted by {admin} for {duration}",
            user=message.reply_to_message.from_user.id,
            admin=message.from_user.id,
            duration=duration,
        )
    except BadRequest as e:
        logger.error("Failed to restrict chat member: {error!r}", error=e)
        return False
    else:
        await ModeratorEvent.save_new_action(
            moderator=message.from_user,
            user=message.reply_to_message.from_user,
            chat=chat,
            type_restriction="ro",
            duration=duration,
            comment=comment
        )

    await message.reply(
        "Пользователь {user} сможет <b>только читать</b> сообщения на протяжении {duration}".format(
            user=message.reply_to_message.from_user.get_mention(),
            duration=format_timedelta(duration),
        )
    )


@dp.message_handler(
    commands=["ban"],
    commands_prefix="!",
    is_reply=True,
    user_can_restrict_members=True,
    bot_can_restrict_members=True,
)
async def cmd_ban(message: types.Message, chat: Chat):
    duration_text, comment = get_moderator_message_args(message.text)
    if duration_text:
        try:
            duration = parse_timedelta_from_text(duration_text)
        except TimedeltaParseError as e:
            return await message.reply(f"Не могу распознать время. {quote_html(e.text)}")
    else:
        duration = DEFAULT_DURATION

    try:
        await message.chat.kick(message.reply_to_message.from_user.id, until_date=duration)
        logger.info(
            "User {user} kicked by {admin} for {duration}",
            user=message.reply_to_message.from_user.id,
            admin=message.from_user.id,
            duration=duration,
        )
    except BadRequest as e:
        logger.error("Failed to kick chat member: {error!r}", error=e)
        return False
    else:
        await ModeratorEvent.save_new_action(
            moderator=message.from_user,
            user=message.reply_to_message.from_user,
            chat=chat,
            type_restriction="ban",
            duration=duration,
            comment=comment
        )

    text = "Пользователь {user} попал в бан этого чата.".format(
            user=message.reply_to_message.from_user.get_mention(),
        )
    if duration < FOREVER_DURATION:
        text += " Он сможет вернуться через {duration}".format(duration=format_timedelta(duration))
    await message.reply(text)


@dp.message_handler(
    commands=["ro", "mute", "ban"],
    commands_prefix="!",
    is_reply=True,
    user_can_restrict_members=True,
)
async def cmd_ro_bot_not_admin(message: types.Message):
    await message.reply("Чтобы я выполнял функции модератора, дайте мне соотвествующие права")


@dp.message_handler(
    commands=["ro", "mute", "ban"],
    commands_prefix="!",
    bot_can_delete_messages=True,
)
async def cmd_ro_bot_not_admin(message: types.Message):
    await message.delete()


@dp.message_handler(
    commands=["w", "warn"],
    commands_prefix="!",
    is_reply=True,
    user_can_restrict_members=True,
)
async def cmd_warn(message: types.Message, chat: Chat):
    args = message.text.split(maxsplit=1)
    if len(args) == 1:
        comment = ""
    else:
        comment = args[1]

    await ModeratorEvent.save_new_action(
        moderator=message.from_user,
        user=message.reply_to_message.from_user,
        chat=chat,
        type_restriction="warn",
        comment=comment
    )

    text = "Пользователь {user} получил официальное предупреждение от модератора".format(
        user=message.reply_to_message.from_user.get_mention(),
    )
    await message.reply(text)


@dp.message_handler(commands="info", commands_prefix='!', is_reply=True)
async def get_info_about_user(message: types.Message, chat: Chat):
    target_user = await User.get_or_create_from_tg_user(message.reply_to_message.from_user)
    info = await get_user_info(target_user, chat)
    try:
        await bot.send_message(
            message.from_user.id,
            f"Данные на {target_user.mention_link}:\n" + "\n".join(info),
            disable_web_page_preview=True
        )
    except Unauthorized:
        await message.reply("Напишите мне в личку /start и повторите команду.")
    finally:
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            await message.delete()
