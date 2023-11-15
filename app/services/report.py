from datetime import datetime
from typing import Iterable, Literal

import aiogram
from aiogram import Bot

from app.infrastructure.database.models import Chat, Report, ReportStatus, User
from app.infrastructure.database.repo.report import ReportRepo
from app.services.change_karma import change_karma
from app.services.remove_message import delete_message_by_id
from app.utils.types import ResultChangeKarma


async def register_report(
    reporter: User,
    reported_user: User,
    chat: Chat,
    reported_message: aiogram.types.Message,
    command_message: aiogram.types.Message,
    report_repo: ReportRepo,
) -> Report:
    report = await report_repo.create(
        reporter=reporter,
        reported_user=reported_user,
        chat=chat,
        reported_message=reported_message,
        command_message=command_message,
        status=ReportStatus.PENDING,
    )
    return report


async def resolve_report(
    report_id: int,
    resolved_by: User,
    resolution: Literal[ReportStatus.APPROVED, ReportStatus.DECLINED],
    report_repo: ReportRepo,
) -> tuple[Report, ...]:
    """
    Resolve all pending reports that are linked to the same message. All linked
    reports except the first one are resolved as cancelled.
    Returns all linked reports.
    """
    resolution_time = datetime.utcnow()
    first_report, *linked_reports = await report_repo.get_linked_pending_reports(
        report_id
    )

    first_report.resolved_by = resolved_by
    first_report.status = resolution
    first_report.resolution_time = resolution_time

    if not linked_reports:
        await report_repo.update(first_report)
        return (first_report,)

    for report in linked_reports:
        report.resolved_by = resolved_by
        report.status = ReportStatus.CANCELLED
        report.resolution_time = resolution_time

    await report_repo.update(
        first_report,
        *linked_reports,
        fields=("resolved_by", "status", "resolution_time"),
    )
    return first_report, *linked_reports


async def cancel_report(
    report_id: int,
    resolved_by: User,
    report_repo: ReportRepo,
) -> Report:
    report = await report_repo.get_report_by_id(report_id)

    report.resolved_by = resolved_by
    report.resolution_time = datetime.utcnow()
    report.status = ReportStatus.CANCELLED

    await report_repo.update(report)
    return report


async def set_report_bot_reply(
    report: Report, bot_reply: aiogram.types.Message, report_repo: ReportRepo
):
    report.bot_reply_message_id = bot_reply.message_id
    await report_repo.update(report)


async def reward_reporter(
    reporter_id: int, reward_amount: int, chat: Chat, bot: Bot
) -> ResultChangeKarma:
    from_user = await User.get_or_create_from_tg_user(await bot.get_me())
    target_user = await User.get(id=reporter_id)
    return await change_karma(
        user=from_user,
        target_user=target_user,
        chat=chat,
        how_change=reward_amount,
        bot=bot,
        comment="Report reward",
        is_reward=True,
    )


async def cleanup_reports_dialog(
    first_report: Report,
    linked_reports: Iterable[Report],
    delete_first_reply: bool,
    bot: Bot,
):
    await delete_message_by_id(
        first_report.chat.chat_id, first_report.command_message_id, bot
    )

    if delete_first_reply:
        await delete_message_by_id(
            first_report.chat.chat_id, first_report.bot_reply_message_id, bot
        )

    for report in linked_reports:
        await delete_message_by_id(report.chat.chat_id, report.command_message_id, bot)
        await delete_message_by_id(
            report.chat.chat_id, report.bot_reply_message_id, bot
        )
