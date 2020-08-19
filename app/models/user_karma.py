from math import sqrt

from tortoise import fields
from tortoise.models import Model

from app.utils.exceptions import SubZeroKarma
from .chat import Chat
from .user import User


class UserKarma(Model):
    """
    information about (karma) (user) in (chat)
    """
    uc_id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField('models.User', related_name='karma')
    chat: fields.ForeignKeyRelation[Chat] = fields.ForeignKeyField('models.Chat', related_name='user_karma')
    karma = fields.FloatField(default=1)

    class Meta:
        table = 'user_karma'
        unique_together = ('user', 'chat')

    def __str__(self):
        # noinspection PyUnresolvedReferences
        rez = f'UserKarma: id{self.uc_id}, karma: {self.karma}, user_id {self.user_id}, chat_id {self.chat_id}'
        return rez

    def __repr__(self):
        return str(self)

    async def change(self, user_changed: User, how_change: float):
        """
        change karma to (self.user) from (user_changed)
        (how_change) must be from -1 to +1 (power from -100% to +100 %)
        """
        if abs(how_change) != 1:
            raise ValueError(f"how_change must be +1 or -1 but it is {how_change}")
        await self.fetch_related('chat')
        power = await self.get_power(user_changed, self.chat)
        if power < 0.01:
            raise SubZeroKarma(
                "User have to small karma",
                user_id=user_changed.id,
                chat_id=self.chat.chat_id
            )
        self.karma = self.karma + how_change * power
        await self.save(update_fields=["karma"])
        return power

    @classmethod
    async def change_or_create(cls, target_user: User, chat: Chat, user_changed: User, how_change: float):
        """
        change karma to (target_user) from (user_changed) in (chat)
        (how_change) must be from -1 to +1 (power from -100% to +100 %)
        """
        uk, _ = await UserKarma.get_or_create(
            user=target_user,
            chat=chat
        )
        power = await uk.change(user_changed=user_changed, how_change=how_change)
        return uk, power

    @classmethod
    async def get_power(cls, user: User, chat: Chat) -> float:
        uk, _ = await cls.get_or_create(user=user, chat=chat)
        return uk.power

    @property
    def power(self) -> float:
        if self.karma <= 0.0:
            return 0
        return sqrt(self.karma)

    @property
    def karma_round(self) -> float:
        return round(self.karma, 2)

    @classmethod
    async def all_to_json(cls, chat_id: int = None) -> dict:
        if chat_id is not None:
            uks = await cls.filter(chat_id=chat_id).prefetch_related("user").order_by("-karma")
            return {
                chat_id: [
                    {**uk.user.to_json(), "karma": uk.karma} for uk in uks
                ]
            }
        else:
            all_data = {}
            for chat in await Chat.all():
                all_data.update(await cls.all_to_json(chat.chat_id))
            return all_data
