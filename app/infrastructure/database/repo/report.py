from typing import Iterable

import aiogram
from tortoise import BaseDBAsyncClient

from app.infrastructure.database.models import Chat, Report, ReportStatus, User


class ReportRepo:
    def __init__(self, session: BaseDBAsyncClient | None = None):
        self.session = session

    async def create(
        self,
        reporter: User,
        reported_user: User,
        chat: Chat,
        reported_message: aiogram.types.Message,
        command_message: aiogram.types.Message,
        status: ReportStatus,
    ) -> Report:
        report = await Report.create(
            reporter=reporter,
            reported_user=reported_user,
            chat=chat,
            created_time=command_message.date,
            command_message_id=command_message.message_id,
            reported_message_id=reported_message.message_id,
            reported_message_content=reported_message.html_text,
            status=status,
            using_db=self.session,
        )
        return report

    async def save(self, report: Report, fields: Iterable[str] | None = None):
        await report.save(update_fields=fields, using_db=self.session)

    async def get_report_by_id(self, report_id: int) -> Report:
        return await Report.get(id=report_id, using_db=self.session)

    async def get_linked_pending_reports(self, report_id: int) -> Iterable[Report]:
        report = await Report.get(id=report_id, using_db=self.session).prefetch_related("chat")
        return await (
            Report.filter(
                chat=report.chat,
                reported_message_id=report.reported_message_id,
                status=ReportStatus.PENDING,
            )
            .prefetch_related("chat", "reporter")
            # Sort by `created_time` and command_message_id to get the first report
            # If `created_time` is the same,
            # the first report is the one with the lowest `command_message_id`
            .order_by("created_time", "command_message_id")
            .using_db(self.session)
            .all()
        )

    async def has_resolved_report(self, chat_id: int, message_id: int) -> bool:
        """Return True, if provided message has reports with status Approved or Declined"""
        return await (
            Report.filter(
                chat__chat_id=chat_id,
                reported_message_id=message_id,
                status__in=[ReportStatus.APPROVED.value, ReportStatus.DECLINED.value],
            )
            .using_db(self.session)
            .exists()
        )
