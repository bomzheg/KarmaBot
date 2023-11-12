from enum import Enum

from tortoise import fields
from tortoise.models import Model

from app.infrastructure.database.models.chat import Chat
from app.infrastructure.database.models.user import User

TG_MESSAGE_MAX_LEN = 4096


class ReportStatus(Enum):
    APPROVED = "approved"
    DECLINED = "declined"
    PENDING = "pending"
    CANCELLED = "cancelled"


class Report(Model):
    id = fields.IntField(pk=True)
    reporter: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="made_reports"
    )
    reported_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="got_reports"
    )
    chat: fields.ForeignKeyRelation[Chat] = fields.ForeignKeyField(
        "models.Chat", related_name="reports"
    )
    created_time = fields.DatetimeField(auto_now=True, null=False)
    resolution_time = fields.DatetimeField(null=True)
    reported_message_id = fields.BigIntField(generated=False, null=False)
    reported_message_content = fields.CharField(null=False, max_length=TG_MESSAGE_MAX_LEN)
    resolved_by: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="resolved_reports", null=True
    )
    status = fields.CharEnumField(ReportStatus, null=False)

    class Meta:
        table = "reports"
