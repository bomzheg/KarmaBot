import typing
from enum import Enum

from aiogram.utils.text_decorations import html_decoration as hd
from tortoise import fields
from tortoise.models import Model


class ChatType(str, Enum):
    private = "private"
    group = "group"
    supergroup = "supergroup"
    channel = 'channel'


class Chat(Model):
    chat_id = fields.BigIntField(pk=True, generated=False)
    type_: ChatType = typing.cast(ChatType, fields.CharEnumField(ChatType))
    title = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=32, null=True)
    description = fields.CharField(max_length=255, null=True)
    # noinspection PyUnresolvedReferences
    user_karma: fields.ReverseRelation['UserKarma']  # noqa: F821
    # noinspection PyUnresolvedReferences
    settings: fields.ReverseRelation['ChatSettings']  # noqa: F821

    class Meta:
        table = "chats"

    @property
    def mention(self):
        return hd.link(hd.quote(self.title), f"t.me/{self.username}") if self.username else hd.quote(self.title)

    def __str__(self):
        rez = f"Chat with type: {self.type_} with ID {self.chat_id}, title: {self.title}"
        if self.username:
            rez += f" Username @{self.username}"
        if self.description:
            rez += f". description: {self.description}"
        return rez

    def __repr__(self):
        return str(self)
