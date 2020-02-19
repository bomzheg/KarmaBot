from math import log10

from tortoise import fields
from tortoise.models import Model
from loguru import logger

from .chat import Chat
from .user import User


class UserKarma(Model):
    uc_id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField('models.User', related_name='karma')
    chat: fields.ForeignKeyRelation[Chat] = fields.ForeignKeyField('models.Chat', related_name='user_karma')
    karma = fields.FloatField(default=1)

    class Meta:
        table = 'user_karma'

    def __str__(self):
        rez = str(self.uc_id)
        return rez

    def __repr__(self):
        return str(self)

    async def up(self, user_changed: User):
        await self.fetch_related('chat')
        power = await self.get_power(user_changed, self.chat)
        self.karma += power
        await self.save()

    async def down(self, user_changed: User):
        await self.fetch_related('chat')
        power = await self.get_power(user_changed, self.chat)
        self.karma -= power
        await self.save()

    @classmethod
    async def get_power(cls, user: User, chat: Chat) -> float:
        uk, _ = await cls.get_or_create(user=user, chat=chat)
        if uk.karma < 0.0:
            return 0
        if uk.karma <= 1.0:
            return 1
        return log10(uk.karma + 1)
    @property
    def karma_round(self):
        return round(self.karma, 2)
