import asyncio

from aiogram import Bot, F, Router, types
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.filters import Command, CommandObject, MagicData
from aiogram.utils.text_decorations import html_decoration as hd

from app.filters import (
    BotHasPermissions,
    HasPermissions,
    HasTargetFilter,
    TargetHasPermissions,
)
from app.filters.reports import HasResolvedReport
from app.handlers import keyboards as kb
from app.infrastructure.database.models import Chat, ChatSettings, ReportStatus, User
from app.infrastructure.database.repo.report import ReportRepo
from app.infrastructure.database.repo.user import UserRepo
from app.models.config import Config
from app.services.moderation import (
    ban_user,
    delete_moderator_event,
    get_duration,
    get_mentions_admins,
    ro_user,
    warn_user,
)
from app.services.remove_message import (
    cleanup_command_dialog,
    delete_message,
    remove_kb,
)
from app.services.report import (
    cancel_report,
    cleanup_reports_dialog,
    register_report,
    resolve_report,
    reward_reporter,
    set_report_bot_reply,
)
from app.services.user_info import get_user_info
from app.utils.exceptions import ModerationError, TimedeltaParseError
from app.utils.log import Logger
from app.utils.view import hidden_link

logger = Logger(__name__)
router = Router(name=__name__)


@router.message(
    F.chat.type.in_(["group", "supergroup"]),
    HasTargetFilter(),
    ~HasResolvedReport(),
    Command("report", "admin", "spam", prefix="/!@"),
)
async def report_message(
    message: types.Message,
    chat: Chat,
    user: User,
    target: User,
    bot: Bot,
    report_repo: ReportRepo,
):
    logger.info(
        "User {user} reported message {message} in chat {chat}",
        user=message.from_user.id,
        message=message.message_id,
        chat=message.chat.id,
    )
    answer_message = "Спасибо за сообщение. Мы обязательно разберёмся"
    admins_mention = await get_mentions_admins(message.chat, bot)

    report = await register_report(
        reporter=user,
        reported_user=target,
        chat=chat,
        reported_message=message.reply_to_message,
        command_message=message,
        report_repo=report_repo,
    )

    reaction_keyboard = kb.get_report_reaction_kb(report=report, user=user)
    bot_reply = await message.reply(
        f"{answer_message}.{admins_mention}", reply_markup=reaction_keyboard
    )
    await set_report_bot_reply(report, bot_reply, report_repo)


@router.message(
    F.chat.type.in_(["group", "supergroup"]),
    HasTargetFilter(),
    HasResolvedReport(),
    Command("report", "admin", "spam", prefix="/!@"),
)
async def report_already_reported(message: types.Message, config: Config, bot: Bot):
    reply = await message.reply("Сообщение уже было рассмотрено ранее")
    return asyncio.create_task(
        cleanup_command_dialog(
            bot=bot,
            bot_message=reply,
            delete_bot_reply=True,
            delay=config.time_to_remove_temp_messages,
        )
    )


@router.message(
    F.chat.type == "private",
    Command("report", "admin", "spam", prefix="/!@"),
)
async def report_private(message: types.Message):
    await message.reply(
        "Вы можете жаловаться на сообщения пользователей только в группах."
    )


@router.message(
    F.chat.type.in_(["group", "supergroup"]),
    HasTargetFilter(),
    Command(commands=["ro", "mute"], prefix="!"),
    HasPermissions(can_restrict_members=True),
    ~TargetHasPermissions(),
    BotHasPermissions(can_restrict_members=True),
)
async def cmd_ro(
    message: types.Message, user: User, target: User, chat: Chat, bot: Bot
):
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
    F.chat.type.in_(["group", "supergroup"]),
    Command(commands=["ro", "mute"], prefix="!"),
    HasPermissions(can_restrict_members=True),
    ~BotHasPermissions(can_restrict_members=True),
)
async def cmd_ro_no_bot_permissions(message: types.Message):
    await message.reply(
        "Мне нужны соответствующие права, чтобы запрещать писать пользователям в группе."
    )


@router.message(
    F.chat.type == "private",
    Command(commands=["ro", "mute"], prefix="!"),
)
async def cmd_ro_private(message: types.Message):
    await message.reply("Вы можете запрещать писать пользователям только в группах.")


@router.message(
    F.chat.type.in_(["group", "supergroup"]),
    HasTargetFilter(),
    Command(commands=["ban"], prefix="!"),
    HasPermissions(can_restrict_members=True),
    ~TargetHasPermissions(),
    BotHasPermissions(can_restrict_members=True),
)
async def cmd_ban(
    message: types.Message, user: User, target: User, chat: Chat, bot: Bot
):
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
    F.chat.type.in_(["group", "supergroup"]),
    Command(commands=["ban"], prefix="!"),
    HasPermissions(can_restrict_members=True),
    ~BotHasPermissions(can_restrict_members=True),
)
async def cmd_ban_no_bot_permissions(message: types.Message):
    await message.reply(
        "Мне нужны соответствующие права, чтобы блокировать пользователей в группе."
    )


@router.message(
    F.chat.type == "private",
    Command(commands=["ban"], prefix="!"),
)
async def cmd_ban_private(message: types.Message):
    await message.reply("Вы можете блокировать пользователей только в группах.")


@router.message(
    F.chat.type.in_(["group", "supergroup"]),
    HasTargetFilter(),
    Command(commands=["w", "warn"], prefix="!"),
    HasPermissions(can_restrict_members=True),
)
async def cmd_warn(
    message: types.Message,
    chat: Chat,
    target: User,
    user: User,
    config: Config,
    command: CommandObject,
):
    comment = command.args or ""

    moderator_event = await warn_user(
        moderator=user, target_user=target, chat=chat, comment=comment
    )

    text = (
        "Пользователь {user} получил официальное предупреждение от модератора".format(
            user=target.mention_link,
        )
    )
    msg = await message.reply(
        text,
        reply_markup=kb.get_kb_warn_cancel(user=user, moderator_event=moderator_event),
    )

    asyncio.create_task(remove_kb(msg, config.time_to_cancel_actions))


@router.message(
    F.chat.type == "private",
    Command(commands=["w", "warn"], prefix="!"),
)
async def cmd_warn_private(message: types.Message):
    await message.reply(
        "Вы можете выдавать предупреждения пользователям только в группах."
    )


@router.message(
    F.chat.type == "private",
    Command("info", prefix="!"),
)
async def get_info_about_user_private(message: types.Message):
    await message.reply(
        "Вы можете запрашивать информацию о пользователях только в группах."
    )


@router.message(
    F.chat.type.in_(["group", "supergroup"]),
    Command("info", prefix="!"),
    HasTargetFilter(can_be_same=True),
)
async def get_info_about_user(
    message: types.Message,
    chat: Chat,
    target: User,
    config: Config,
    bot: Bot,
    user_repo: UserRepo,
):
    info = await get_user_info(target, chat, config.date_format)
    target_karma = await user_repo.get_karma(target, chat)
    if target_karma is None:
        target_karma = "пока не имеет кармы"
    information = f"Данные на {target.mention_link} ({target_karma}):\n" + "\n".join(
        info
    )
    try:
        await bot.send_message(
            message.from_user.id, information, disable_web_page_preview=True
        )
    except TelegramUnauthorizedError:
        me = await bot.me()
        await message.reply(
            f"{message.from_user.mention_html()}, напишите мне в личку "
            f'<a href="https://t.me/{me.username}?start">/start</a> и повторите команду.'
        )
    finally:
        await delete_message(message)


@router.message(
    F.chat.type.in_(["group", "supergroup"]),
    Command(commands=["ro", "mute", "ban", "warn", "w"], prefix="!"),
    BotHasPermissions(can_delete_messages=True),
)
async def cmd_unhandled(message: types.Message):
    """
    Событие не было обработано ни одним из обработчиков.

    Это может произойти, если пользователь не имеет прав на выполнение одной из команд,
    либо если происходит попытка применить ограничения на администратора, себя или бота.
    """
    await delete_message(message)


@router.callback_query(
    kb.WarnCancelCb.filter(), MagicData(F.user.tg_id == F.callback_data.user_id)
)
async def cancel_warn(
    callback_query: types.CallbackQuery, callback_data: kb.WarnCancelCb, bot: Bot
):
    from_user = callback_query.from_user
    await delete_moderator_event(callback_data.moderator_event_id, moderator=from_user)

    await callback_query.answer("Вы отменили предупреждение", show_alert=True)
    await cleanup_command_dialog(
        bot, bot_message=callback_query.message, delete_bot_reply=True
    )


@router.callback_query(
    kb.ApproveReportCb.filter(),
    HasPermissions(can_restrict_members=True),
)
async def approve_report_handler(
    callback_query: types.CallbackQuery,
    callback_data: kb.ApproveReportCb,
    user: User,
    chat: Chat,
    bot: Bot,
    config: Config,
    chat_settings: ChatSettings,
    report_repo: ReportRepo,
    user_repo: UserRepo,
):
    logger.info(
        "Moderator {moderator} approved report {report}",
        moderator=callback_query.from_user.id,
        report=callback_data.report_id,
    )
    first_report, *linked_reports = await resolve_report(
        report_id=callback_data.report_id,
        resolved_by=user,
        resolution=ReportStatus.APPROVED,
        report_repo=report_repo,
    )
    award_enabled = chat_settings.karma_counting and chat_settings.report_karma_award
    if award_enabled:
        karma_change_result = await reward_reporter(
            reporter_id=first_report.reporter.id,
            chat=chat,
            reward_amount=chat_settings.report_karma_award,
            bot=bot,
            user_repo=user_repo,
        )
        message = await bot.edit_message_text(
            "<b>{reporter}</b> получил <b>+{reward_amount}</b> кармы "
            "в награду за репорт{admin_url}".format(
                reporter=hd.quote(karma_change_result.karma_event.user_to.fullname),
                reward_amount=chat_settings.report_karma_award,
                admin_url=hidden_link(user.link),
            ),
            chat_id=first_report.chat.chat_id,
            message_id=first_report.bot_reply_message_id,
        )
        if config.report_award_cleanup_delay > 0:
            asyncio.create_task(
                delete_message(
                    message,
                    sleep_time=config.report_award_cleanup_delay,
                )
            )

    await callback_query.answer("Вы подтвердили репорт", show_alert=not award_enabled)
    await cleanup_reports_dialog(
        first_report=first_report,
        linked_reports=linked_reports,
        delete_first_reply=not award_enabled,
        bot=bot,
    )


@router.callback_query(
    kb.DeclineReportCb.filter(), HasPermissions(can_restrict_members=True)
)
async def decline_report_handler(
    callback_query: types.CallbackQuery,
    callback_data: kb.DeclineReportCb,
    user: User,
    bot: Bot,
    report_repo: ReportRepo,
):
    logger.info(
        "Moderator {moderator} declined report {report}",
        moderator=callback_query.from_user.id,
        report=callback_data.report_id,
    )
    first_report, *linked_reports = await resolve_report(
        report_id=callback_data.report_id,
        resolved_by=user,
        resolution=ReportStatus.DECLINED,
        report_repo=report_repo,
    )
    await callback_query.answer("Вы отклонили репорт", show_alert=True)
    await cleanup_reports_dialog(
        first_report, linked_reports, delete_first_reply=True, bot=bot
    )


@router.callback_query(
    kb.CancelReportCb.filter(), MagicData(F.user.id == F.callback_data.reporter_id)
)
async def cancel_report_handler(
    callback_query: types.CallbackQuery,
    callback_data: kb.CancelReportCb,
    user: User,
    report_repo: ReportRepo,
    bot: Bot,
):
    logger.info(
        "User {user} cancelled report {report}",
        user=callback_query.from_user.id,
        report=callback_data.report_id,
    )
    await cancel_report(
        report_id=callback_data.report_id,
        resolved_by=user,
        report_repo=report_repo,
    )
    await callback_query.answer("Вы отменили репорт", show_alert=True)
    await cleanup_command_dialog(
        bot, bot_message=callback_query.message, delete_bot_reply=True
    )


@router.callback_query(
    kb.WarnCancelCb.filter(),
    MagicData(F.callback_data.user_id != F.callback_query.from_user.id),
)
@router.callback_query(
    kb.CancelReportCb.filter(), MagicData(F.user.id != F.callback_data.reporter_id)
)
@router.callback_query(
    kb.ApproveReportCb.filter(), ~HasPermissions(can_restrict_members=True)
)
@router.callback_query(
    kb.DeclineReportCb.filter(), ~HasPermissions(can_restrict_members=True)
)
async def unauthorized_button_action(
    callback_query: types.CallbackQuery, config: Config
):
    await callback_query.answer(
        "Эта кнопка не для Вас", cache_time=config.callback_query_answer_cache_time
    )
