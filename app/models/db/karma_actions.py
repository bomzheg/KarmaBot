from aiogram.utils.markdown import quote_html
from tortoise import fields
from tortoise.models import Model

from .chat import Chat
from .user import User


class KarmaEvent(Model):
    id_ = fields.IntField(pk=True, source_field="id")
    user_from: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User', related_name='i_change_karma_events')
    user_to: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User', related_name='my_karma_events')
    chat: fields.ForeignKeyRelation[Chat] = fields.ForeignKeyField(
        'models.Chat', related_name='karma_events')
    date = fields.DatetimeField(auto_now=True, null=False)
    how_change = fields.FloatField(
        description="how match change karma in percent of possible power"
    )
    how_change_absolute = fields.FloatField(
        description="how match user_from change karma user_to in absolute",
        source_field="how_match_change"
    )
    comment = fields.TextField(null=True)

    class Meta:
        table = 'karma_events'

    def __repr__(self):
        return (
            f"KarmaEvent {self.id_} from user {self.user_from.id} to {self.user_to.id}, "
            f"date {self.date}, change {self.how_change}"
        )

    @classmethod
    async def get_last_by_user(cls, user: User, chat: Chat, limit: int = 10):
        return await cls.filter(
            user_to=user,
            chat=chat
        ).order_by('-date').limit(limit).prefetch_related("user_from").all()

    def format_event(self, date_format: str):
        rez = (
            f"{self.date.date().strftime(date_format)} "
            f"{get_emoji_by_karma_sign(self.how_change_absolute)}"
            f"{self.user_from.mention_no_link} изменил карму на "
            f"{self.how_change_absolute:.2f} ({self.how_change:.0%} своей силы.) "
        )
        if self.comment:
            rez += f'"{quote_html(self.comment)}"'
        return rez


def get_emoji_by_karma_sign(value: float):
    if value > 0:
        return "⏫"
    if value < 0:
        return "⏬"
    return ""
