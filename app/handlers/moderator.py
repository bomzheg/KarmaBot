from aiogram import types
from aiogram.utils.exceptions import Unauthorized
from aiogram.utils.markdown import hide_link, quote_html
from loguru import logger

from app.misc import dp, bot
from app.utils.exceptions import TimedeltaParseError, ModerationError
from app.models import Chat, User
from app.services.user_info import get_user_info
from app.services.moderation import warn_user, ro_user, ban_user, get_duration
from app.services.remove_message import delete_message


@dp.message_handler(
    types.ChatType.is_group_or_super_group,
    is_reply=True,
    commands=['report', 'admin'],
    commands_prefix="/!@",
)
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
    has_target=True,
    user_can_restrict_members=True,
    bot_can_restrict_members=True,
)
async def cmd_ro(message: types.Message, user: User, target: User):
    try:
        duration, comment = get_duration(message.text)
    except TimedeltaParseError as e:
        return await message.reply(f"Не могу распознать время. {quote_html(e.text)}")

    try:
        success_text = await ro_user(message.chat, target, user, duration, comment)
    except ModerationError as e:
        logger.error(e)
    else:
        await message.reply(success_text)


@dp.message_handler(
    commands=["ban"],
    commands_prefix="!",
    has_target=True,
    user_can_restrict_members=True,
    bot_can_restrict_members=True,
)
async def cmd_ban(message: types.Message, user: User, target: User):
    try:
        duration, comment = get_duration(message.text)
    except TimedeltaParseError as e:
        return await message.reply(f"Не могу распознать время. {quote_html(e.text)}")

    try:
        success_text = await ban_user(message.chat, target, user, duration, comment)
    except ModerationError as e:
        logger.error(e)
    else:
        await message.reply(success_text)


@dp.message_handler(
    commands=["w", "warn"],
    commands_prefix="!",
    has_target=True,
    user_can_restrict_members=True,
)
async def cmd_warn(message: types.Message, chat: Chat, target: User, user: User):
    args = message.text.split(maxsplit=1)
    comment = args[1] if len(args) > 1 else ""

    await warn_user(
        moderator=user,
        target_user=target,
        chat=chat,
        comment=comment
    )

    text = "Пользователь {user} получил официальное предупреждение от модератора".format(
        user=target.mention_link,
    )
    await message.reply(text)


@dp.message_handler(commands="info", commands_prefix='!', has_target=dict(can_be_same=True))
async def get_info_about_user(message: types.Message, chat: Chat, target: User):
    info = await get_user_info(target, chat)
    target_karma = await target.get_karma(chat)
    if target_karma is None:
        target_karma = "пока не имеет кармы"
    information = f"Данные на {target.mention_link} ({target_karma}):\n" + "\n".join(info)
    try:
        await bot.send_message(
            message.from_user.id,
            information,
            disable_web_page_preview=True
        )
    except Unauthorized:
        await message.reply(f"{message.from_user.get_mention()}, напишите мне в личку /start и повторите команду.")
    finally:
        await delete_message(message)


@dp.message_handler(
    commands=["ro", "mute", "ban"],
    commands_prefix="!",
    has_target=True,
    user_can_restrict_members=True,
)
async def cmd_ro_bot_not_admin(message: types.Message):
    """бот без прав модератора"""
    await message.reply("Чтобы я выполнял функции модератора, дайте мне соотвествующие права")


@dp.message_handler(
    commands=["ro", "mute", "ban", "warn"],
    commands_prefix="!",
    bot_can_delete_messages=True,
)
async def cmd_ro_bot_not_admin(message: types.Message):
    """юзер без прав модератора"""
    await delete_message(message)
