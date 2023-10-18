from datetime import datetime

import aiogram
from aiogram import Bot
from tortoise.backends.base.client import BaseDBAsyncClient

from app.models.db import User, Chat
from app.models.db.report import Report, ReportStatus
from app.services.change_karma import change_karma
from app.utils.types import ResultChangeKarma


async def register_report(
        reporter: User,
        reported_user: User,
        chat: Chat,
        reported_message: aiogram.types.Message,
        db_session: BaseDBAsyncClient,
) -> Report:
    report = await Report.create(
        reporter=reporter,
        reported_user=reported_user,
        chat=chat,
        reported_message_id=reported_message.message_id,
        reported_message_content=reported_message.html_text,
        status=ReportStatus.pending,

        using_db=db_session
    )
    return report


async def resolve_report(
        report_id: int,
        moderator: User,
        resolution: ReportStatus,
        db_session: BaseDBAsyncClient
):
    report = await Report.get(id=report_id, using_db=db_session)
    report.reacted_moderator = moderator
    report.status = resolution
    report.resolution_time = datetime.utcnow()
    await report.save(using_db=db_session)


async def reward_reporter(
        reporter_id: int,
        reward_amount: int,
        chat: Chat,
        bot: Bot
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
        is_reward=True
    )
