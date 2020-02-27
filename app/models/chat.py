import typing
from enum import Enum

from loguru import logger
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model


class ChatType(str, Enum):
    private = "private"
    group = "group"
    supergroup = "supergroup"
    channel = 'channel'


class Chat(Model):
    chat_id = fields.BigIntField(pk=True, generated=False)
    type_: ChatType = typing.cast(ChatType, fields.CharEnumField(ChatType))
    title = fields.CharField(max_length=255)
    username = fields.CharField(max_length=32, null=True)
    description = fields.CharField(max_length=255, null=True)
    user_karma: fields.ReverseRelation['UserKarma']

    class Meta:
        table = "chats"

    @classmethod
    async def create_from_tg_chat(cls, chat):
        chat = await cls.create(
            chat_id=chat.id,
            type_=chat.type,
            title=chat.title,
            username=chat.username
        )
        return chat

    @classmethod
    async def get_or_create_from_tg_chat(cls, chat):
        try:
            chat = await cls.get(chat_id=chat.id)
        except DoesNotExist:
            chat = await cls.create_from_tg_chat(chat=chat)
        return chat

    def __str__(self):
        rez = f"Chat with type: {self.type_} with ID {self.chat_id}, title: {self.title}"
        if self.username:
            rez += f" Username @{self.username}"
        if self.description:
            rez += f". description: {self.description}"
        return rez

    def __repr__(self):
        return str(self)

    async def get_top_karma_list(self, limit: int=15):
        await self.fetch_related('user_karma')
        users_karmas = await self.user_karma.order_by('-karma').limit(limit).all()
        rez = []
        for user_karma in users_karmas:
            user = await user_karma.user.first()
            karma = user_karma.karma_round
            rez.append((user, karma))
        return rez