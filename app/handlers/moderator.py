from aiogram import types
from aiogram.dispatcher.filters.builtin import Text, Command
from aiogram.utils.markdown import hide_link
from loguru import logger

from app.misc import dp


async def report_filter(message: types.Message):
    if not types.ChatType.is_group_or_super_group(message):
        return False
    if not message.reply_to_message:
        return False
    if await Text(equals='@admin', ignore_case=True).check(message):
        return True
    if await Command(commands=['report', 'admin'], prefixes='/!').check(message):
        return True
    return False


@dp.message_handler(report_filter)
@dp.throttled(rate=5)
async def report(message: types.Message):
    logger.info("user {user} report for message {message}", user=message.from_user.id, message=message.message_id)
    answer_template = "Спасибо за сообщение. Мы обязательно разберёмся. "
    admins_mention = await get_mentions_admins(message.chat)
    logger.debug(answer_template + admins_mention)
    # await message.reply(answer_template + admins_mention)


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
