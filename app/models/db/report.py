from enum import Enum

from tortoise import fields
from tortoise.models import Model

from .chat import Chat
from .user import User

TG_MESSAGE_MAX_LEN = 4096


class ReportStatus(Enum):
    approved = "Approved"
    declined = "Declined"
    pending = "Pending"


class Report(Model):
    id = fields.IntField(pk=True)
    reporter: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User',
        related_name='made_reports'
    )
    reported_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User',
        related_name='got_reports'
    )
    chat: fields.ForeignKeyRelation[Chat] = fields.ForeignKeyField(
        'models.Chat',
        related_name='reports'
    )
    created_time = fields.DatetimeField(auto_now=True, null=False)
    resolution_time = fields.DatetimeField(null=True)
    reported_message_id = fields.BigIntField(generated=False, null=False)
    reported_message_content = fields.CharField(null=False, max_length=TG_MESSAGE_MAX_LEN)
    reacted_moderator: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User',
        related_name='reacted_reports',
        null=True
    )
    status = fields.CharEnumField(ReportStatus, null=False)

    class Meta:
        table = 'reports'
