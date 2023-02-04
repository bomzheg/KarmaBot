from aiogram import types, F, Bot, Router
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.filters import Command
from aiogram.utils.text_decorations import html_decoration as hd

from app.filters import HasTargetFilter, HasPermissions, BotHasPermissions
from app.models.config import Config
from app.models.db import Chat, User
from app.services.moderation import warn_user, ro_user, ban_user, get_duration
from app.services.remove_message import delete_message
from app.services.user_info import get_user_info
from app.utils.exceptions import TimedeltaParseError, ModerationError
from app.utils.log import Logger


logger = Logger(__name__)
router = Router(name=__name__)


@router.message(
    F.chat.type.in_(["group", "supergroup"]),
    F.reply_to_message,
    Command('report', 'admin', 'spam', prefix="/!@"),
)
async def report(message: types.Message, bot: Bot):
    logger.info("user {user} report for message {message}", user=message.from_user.id, message=message.message_id)
    answer_template = "Спасибо за сообщение. Мы обязательно разберёмся. "
    admins_mention = await get_mentions_admins(message.chat, bot)
    await message.reply(answer_template + admins_mention + " ")


async def get_mentions_admins(chat: types.Chat, bot: Bot):
    admins = await bot.get_chat_administrators(chat.id)
    admins_mention = ""
    for admin in admins:
        if admin.user.is_bot:
            continue
        if need_notify_admin(admin):
            admins_mention += hd.link("&#8288;", admin.user.url)
    return admins_mention


def need_notify_admin(admin: types.ChatMemberAdministrator | types.ChatMemberOwner):
    return admin.can_delete_messages or admin.can_restrict_members or admin.status == "creator"


@router.message(
    HasTargetFilter(),
    Command(commands=["ro", "mute"], prefix="!"),
    HasPermissions(can_restrict_members=True),
    BotHasPermissions(can_restrict_members=True),
)
async def cmd_ro(message: types.Message, user: User, target: User, chat: Chat, bot: Bot):
    try:
        duration, comment = get_duration(message.text)
    except TimedeltaParseError as e:
        return await message.reply(f"Не могу распознать время. {hd.quote(e.text)}")

    try:
        success_text = await ro_user(chat, target, user, duration, comment, bot)
    except ModerationError as e:
        logger.error("Failed to restrict chat member: {error!r}", error=e)
    else:
        await message.reply(success_text)


@router.message(
    HasTargetFilter(),
    Command(commands=["ban"], prefix="!"),
    HasPermissions(can_restrict_members=True),
    BotHasPermissions(can_restrict_members=True),
)
async def cmd_ban(message: types.Message, user: User, target: User, chat: Chat, bot: Bot):
    try:
        duration, comment = get_duration(message.text)
    except TimedeltaParseError as e:
        return await message.reply(f"Не могу распознать время. {hd.quote(e.text)}")

    try:
        success_text = await ban_user(chat, target, user, duration, comment, bot)
    except ModerationError as e:
        logger.error("Failed to kick chat member: {error!r}", error=e, exc_info=e)
    else:
        await message.reply(success_text)


@router.message(
    HasTargetFilter(),
    Command(commands=["w", "warn"], prefix="!"),
    HasPermissions(can_restrict_members=True),
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


@router.message(HasTargetFilter(can_be_same=True), Command("info", prefix='!'))
async def get_info_about_user(message: types.Message, chat: Chat, target: User, config: Config, bot: Bot):
    info = await get_user_info(target, chat, config.date_format)
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
    except TelegramUnauthorizedError:
        me = await bot.me()
        await message.reply(
            f'{message.from_user.mention_html()}, напишите мне в личку '
            f'<a href="https://t.me/{me.username}?start">/start</a> и повторите команду.'
        )
    finally:
        await delete_message(message)


@router.message(
    HasTargetFilter(),
    Command(commands=["ro", "mute", "ban"], prefix="!"),
    HasPermissions(can_restrict_members=True),
)
async def cmd_ro_bot_not_admin(message: types.Message):
    """бот без прав модератора"""
    await message.reply("Чтобы я выполнял функции модератора, дайте мне соответствующие права")


@router.message(
    Command(commands=["ro", "mute", "ban", "warn", "w"], prefix="!"),
    BotHasPermissions(can_delete_messages=True),
)
async def cmd_ro_bot_not_admin(message: types.Message):
    """юзер без прав модератора"""
    await delete_message(message)
