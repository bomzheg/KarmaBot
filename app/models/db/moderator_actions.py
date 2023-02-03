from datetime import timedelta

from aiogram.utils.text_decorations import html_decoration as hd
from tortoise import fields
from tortoise.models import Model

from app.utils.timedelta_functions import format_timedelta
from .chat import Chat
from .user import User
from ..common import TypeRestriction


class ModeratorEvent(Model):
    id_ = fields.IntField(pk=True, source_field="id")
    moderator: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User', related_name='my_moderator_events')
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User', related_name='my_restriction_events')
    chat: fields.ForeignKeyRelation[Chat] = fields.ForeignKeyField(
        'models.Chat', related_name='moderator_events')
    date = fields.DatetimeField(auto_now=True, null=False)
    type_restriction = fields.CharField(max_length=20)
    timedelta_restriction = fields.TimeDeltaField(null=True)
    comment = fields.TextField(null=True)

    class Meta:
        table = 'moderator_events'

    def __repr__(self):
        # noinspection PyUnresolvedReferences
        return (
            f"ModeratorEvent {self.id_} from moderator {self.moderator_id} to {self.user_id}, date {self.date}, "
            f"type_restriction {self.type_restriction} timedelta_restriction {self.timedelta_restriction}"
        )

    @classmethod
    async def save_new_action(
            cls,
            moderator: User,
            user: User,
            chat: Chat,
            type_restriction: str,
            duration: timedelta = None,
            comment: str = "",
            using_db=None,
    ):
        moderator_event = ModeratorEvent(
            moderator=moderator,
            user=user,
            chat=chat,
            type_restriction=type_restriction,
            timedelta_restriction=duration,
            comment=comment
        )
        await moderator_event.save(using_db=using_db)
        return moderator_event

    @classmethod
    async def get_last_by_user(cls, user: User, chat: Chat, limit: int = 10):
        return await cls.filter(
            user=user,
            chat=chat
        ).order_by('-date').limit(limit).prefetch_related('moderator').all()

    def format_event(self, date_format: str) -> str:
        rez = f"{self.date.date().strftime(date_format)} " \
              f"{TypeRestriction[self.type_restriction].get_emoji()}{self.type_restriction} "

        if self.timedelta_restriction:
            rez += f"{format_timedelta(self.timedelta_restriction)} "

        rez += f"от {self.moderator.mention_no_link}"

        if self.comment:
            rez += f" \"{hd.quote(self.comment)}\""
        return rez
