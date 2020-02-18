from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model


class User(Model):
    user_id = fields.BigIntField(pk=True, generated=False)
    first_name = fields.CharField(max_length=255)
    last_name = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=32, null=True)
    karma = fields.ReverseRelation['user']

    class Meta:
        table = "users"

    @classmethod
    async def create_from_tg_user(cls, user):
        user = await cls.create(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username
        )
        return user

    @classmethod
    async def get_or_create_from_tg_user(cls, user):
        try:
            user = await cls.get(user_id=user.id)
        except DoesNotExist:
            user = await cls.create_from_tg_user(user=user)
        return user

    async def get_small_card(self, no_notification=False):
        if no_notification:
            return await self.get_small_card_no_link()
        else:
            return await self.get_small_card_link()

    async def get_small_card_link(self):
        rez = f"<a href='tg://user?id={self.user_id}'>{self.fullname}</a>"
        if False and self.username:
            rez += f" @{self.username}"
        return rez

    async def get_small_card_no_link(self):
        if self.username:
            rez = f"<a href='t.me/{self.username}'>{self.fullname}</a>"
        else:
            rez = self.fullname
        return rez

    def get_fullname(self):
        name = self.first_name
        if self.last_name is not None:
            name += f" {self.last_name}"
        return name

    def __str__(self):
        rez = f"User ID {self.user_id}, by name {self.first_name} {self.last_name}"
        if self.username:
            rez += f" with username @{self.username}"
        return rez

    def __repr__(self):
        return str(self)

    fullname = property(get_fullname)
