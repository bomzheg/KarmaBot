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
            command_message_id=command_message.id,
            reported_message_id=reported_message.message_id,
            reported_message_content=reported_message.html_text,
            status=status,
            using_db=self.session,
        )
        return report

    async def update(self, *reports: Report, fields: Iterable[str] | None = None):
        if len(reports) == 1:
            await reports[0].save()
        else:
            await Report.bulk_update(reports, fields, using_db=self.session)

    async def get_report_by_id(self, report_id: int) -> Report:
        return await Report.get(id=report_id, using_db=self.session)

    async def get_linked_pending_reports(self, report_id: int) -> Iterable[Report]:
        report = await Report.get(id=report_id, using_db=self.session).prefetch_related(
            "chat"
        )
        return await (
            Report.filter(
                chat=report.chat,
                reported_message_id=report.reported_message_id,
                status=ReportStatus.PENDING,
            )
            .prefetch_related("chat")
            .order_by("created_time")
            .all()
        )
