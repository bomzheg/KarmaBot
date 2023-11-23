from aiogram import types
from aiogram.filters import BaseFilter

from app.infrastructure.database.models import Chat
from app.infrastructure.database.repo.report import ReportRepo


class HasResolvedReport(BaseFilter):
    """Check if reported message already resolved report"""

    async def __call__(
        self, message: types.Message, chat: Chat, report_repo: ReportRepo
    ) -> bool:
        if not message.reply_to_message:
            return False
        return await report_repo.has_resolved_report(
            chat_id=chat.chat_id, message_id=message.reply_to_message.message_id
        )
