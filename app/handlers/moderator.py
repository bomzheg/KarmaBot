from datetime import timedelta

from aiogram import types
from aiogram.dispatcher.filters.builtin import Text, Command
from aiogram.utils.exceptions import BadRequest
from aiogram.utils.markdown import hide_link
from loguru import logger

from app.misc import dp
from app.utils.timedelta_functions import parse_timedelta_from_message, format_timedelta
FOREVER_DURATION = timedelta(days=366)


async def report_filter(message: types.Message):
    if not types.ChatType.is_group_or_super_group(message):
        return False
    if not message.reply_to_message:
        return False
    if await Command(commands=['report', 'admin'], prefixes='/!@').check(message):
        return True
    if await Text(equals='@admin', ignore_case=True).check(message):
        print("text with @admin 0_o")
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


@dp.message_handler(
    commands=["ro", "mute"],
    commands_prefix="!",
    is_reply=True,
    user_can_restrict_members=True,
    bot_can_restrict_members=True,
)
async def cmd_ro(message: types.Message):
    duration = await parse_timedelta_from_message(message)
    if not duration:
        return

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
async def cmd_ban(message: types.Message):
    duration = await parse_timedelta_from_message(message)
    if not duration:
        return

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
