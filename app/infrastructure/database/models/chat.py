import typing
from enum import Enum

from aiogram.utils.text_decorations import html_decoration as hd
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model
from tortoise.transactions import in_transaction

from app.models.db.db import karma_filters
from app.utils.exceptions import NotHaveNeighbours

SQL_PREV_NEXT = """
SELECT
    prev_user_id,
    next_user_id
FROM (SELECT
        user_id,
        LAG(user_id) OVER(ORDER BY karma) prev_user_id,
        LEAD(user_id) OVER(ORDER BY karma) next_user_id
    FROM user_karma
    WHERE chat_id = ?)
WHERE user_id = ?
"""


class ChatType(str, Enum):
    private = "private"
    group = "group"
    supergroup = "supergroup"
    channel = "channel"


class Chat(Model):
    chat_id = fields.BigIntField(pk=True, generated=False)
    type_: ChatType = typing.cast(ChatType, fields.CharEnumField(ChatType))
    title = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=32, null=True)
    description = fields.CharField(max_length=255, null=True)
    # noinspection PyUnresolvedReferences
    user_karma: fields.ReverseRelation["UserKarma"]  # noqa: F821
    # noinspection PyUnresolvedReferences
    settings: fields.ReverseRelation["ChatSettings"]  # noqa: F821

    class Meta:
        table = "chats"

    @classmethod
    async def create_from_tg_chat(cls, chat):
        chat = await cls.create(
            chat_id=chat.id, type_=chat.type, title=chat.title, username=chat.username
        )
        return chat

    @classmethod
    async def get_or_create_from_tg_chat(cls, chat):
        try:
            chat = await cls.get(chat_id=chat.id)
        except DoesNotExist:
            chat = await cls.create_from_tg_chat(chat=chat)
        return chat

    @property
    def mention(self):
        return (
            hd.link(hd.quote(self.title), f"t.me/{self.username}")
            if self.username
            else hd.quote(self.title)
        )

    def __str__(self):
        rez = f"Chat with type: {self.type_} with ID {self.chat_id}, title: {self.title}"
        if self.username:
            rez += f" Username @{self.username}"
        if self.description:
            rez += f". description: {self.description}"
        return rez

    def __repr__(self):
        return str(self)

    # noinspection PyUnresolvedReferences
    async def get_top_karma_list(self, limit: int = 15):
        await self.fetch_related("user_karma")
        users_karmas = (
            await self.user_karma.order_by(*karma_filters)
            .limit(limit)
            .prefetch_related("user")
            .all()
        )
        rez = []
        for user_karma in users_karmas:
            user = user_karma.user
            karma = user_karma.karma_round
            rez.append((user, karma))

        return rez

    # noinspection PyUnresolvedReferences
    async def get_neighbours(
        self, user
    ) -> tuple["UserKarma", "UserKarma", "UserKarma"]:  # noqa: F821
        prev_id, next_id = await get_neighbours_id(self.chat_id, user.id)
        uk = (
            await self.user_karma.filter(user_id__in=(prev_id, next_id))
            .prefetch_related("user")
            .order_by(*karma_filters)
            .all()
        )

        user_uk = await self.user_karma.filter(user=user).prefetch_related("user").first()
        return uk[0], user_uk, uk[1]


async def get_neighbours_id(chat_id, user_id) -> typing.Tuple[int, int]:
    async with in_transaction() as conn:
        neighbours = await conn.execute_query(SQL_PREV_NEXT, (chat_id, user_id))
        try:
            rez = dict(neighbours[1][0])
        except IndexError:
            raise NotHaveNeighbours
        try:
            rez = int(rez["prev_user_id"]), int(rez["next_user_id"])
        except TypeError:
            raise NotHaveNeighbours
        return rez
