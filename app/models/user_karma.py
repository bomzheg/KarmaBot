from math import sqrt

from loguru import logger
from tortoise import fields
from tortoise.models import Model

from app.utils.exceptions import SubZeroKarma
from .chat import Chat
from .user import User
from .db import karma_filters


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

    async def change(self, user_changed: User, how_change: float, using_db=None):
        """
        change karma to (self.user) from (user_changed)
        (how_change) must be from -inf to +inf
        """
        if how_change == 0:
            raise ValueError(f"how_change must be float and not 0 but it is {how_change}")
        await self.fetch_related('chat', using_db=using_db)
        power = await self.get_power(user_changed, self.chat)
        if power < 0.01:
            logger.info("user {user} try to change karma but have negative karma", user=user_changed.tg_id)
            raise SubZeroKarma(
                "User have to small karma",
                user_id=user_changed.id,
                chat_id=self.chat.chat_id
            )
        change_sign = +1 if how_change > 0 else -1
        abs_how_change = min(abs(how_change), power)
        self.karma = self.karma + change_sign * abs_how_change
        await self.save(update_fields=["karma"], using_db=using_db)
        relative_power = abs_how_change / power
        return change_sign * abs_how_change, change_sign * relative_power

    @classmethod
    async def change_or_create(
            cls,
            target_user: User,
            chat: Chat,
            user_changed: User,
            how_change: float,
            using_db=None,
    ):
        """
        change karma to (target_user) from (user_changed) in (chat)
        (how_change) must be from -inf to +inf
        """
        uk, _ = await UserKarma.get_or_create(
            user=target_user,
            chat=chat,
            using_db=using_db,
        )
        abs_change, relative_change = await uk.change(
            user_changed=user_changed,
            how_change=how_change,
            using_db=using_db,
        )
        return uk, abs_change, relative_change

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

    async def number_in_top(self) -> int:
        # noinspection PyUnresolvedReferences
        return await self.filter(chat_id=self.chat_id, karma__gte=self.karma).count()

    @classmethod
    async def all_to_json(cls, chat_id: int = None) -> dict:
        if chat_id is not None:
            uks = await cls.filter(chat_id=chat_id).prefetch_related("user").order_by(*karma_filters)
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
