from math import sqrt

from tortoise import fields
from tortoise.models import Model

from app.utils.exeptions import SubZeroKarma
from .chat import Chat
from .user import User


class UserKarma(Model):
    uc_id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField('models.User', related_name='karma')
    chat: fields.ForeignKeyRelation[Chat] = fields.ForeignKeyField('models.Chat', related_name='user_karma')
    karma = fields.FloatField(default=1)

    class Meta:
        table = 'user_karma'
        unique_together = ('user', 'chat')

    def __str__(self):
        rez = f'UserKarma: id{self.uc_id}, karma: {self.karma}'
        return rez

    def __repr__(self):
        return str(self)

    async def change(self, user_changed: User, how_change: int):
        """
        change karma to (self.user) from (user_changed)
        (how_change) must be +1 or -1
        """
        await self.fetch_related('chat')
        power = await self.get_power(user_changed, self.chat)
        if power < 0.01:
            raise SubZeroKarma(
                "User have to small karma",
                user_id=user_changed.id,
                chat_id=self.chat.chat_id
            )
        self.karma = self.karma + how_change * power
        await self.save()

    @classmethod
    async def get_power(cls, user: User, chat: Chat) -> float:
        uk, _ = await cls.get_or_create(user=user, chat=chat)
        return uk.power

    @property
    def power(self) -> float:
        if self.karma < 0.0:
            return 0
        if self.karma <= 1.0:
            return 1
        return sqrt(self.karma)

    @property
    def karma_round(self) -> float:
        return round(self.karma, 2)
