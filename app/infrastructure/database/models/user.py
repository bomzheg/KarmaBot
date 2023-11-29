from typing import TYPE_CHECKING

from aiogram.utils.text_decorations import html_decoration as hd
from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from app.infrastructure.database.models.moderator_actions import ModeratorEvent
    from app.infrastructure.database.models.user_karma import UserKarma


class User(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.BigIntField(unique=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=32, null=True)
    is_bot: bool = fields.BooleanField(null=True)
    karma: fields.ReverseRelation["UserKarma"]
    my_restriction_events: fields.ReverseRelation["ModeratorEvent"]

    class Meta:
        table = "users"

    @property
    def mention_link(self):
        return hd.link(hd.quote(self.fullname), self.link)

    @property
    def link(self):
        return f"tg://user?id={self.tg_id}"

    @property
    def mention_no_link(self):
        if self.username:
            rez = hd.link(hd.quote(self.fullname), f"t.me/{self.username}")
        else:
            rez = hd.quote(self.fullname)
        return rez

    @property
    def fullname(self):
        if self.last_name is not None:
            return " ".join((self.first_name, self.last_name))
        return self.first_name or self.username or str(self.tg_id) or str(self.id)

    def to_json(self):
        return dict(
            id=self.id,
            tg_id=self.tg_id,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            is_bot=self.is_bot,
        )

    def __str__(self):
        rez = f"User ID {self.tg_id}, by name {self.first_name} {self.last_name}"
        if self.username:
            rez += f" with username @{self.username}"
        return rez

    def __repr__(self):
        return str(self)
