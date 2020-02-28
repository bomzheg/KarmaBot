from aiogram import types
from loguru import logger
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model
from .chat import Chat
from app.utils.exeptions import UserWithoutUserIdError

class User(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.BigIntField(unique=True, null=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=32, null=True)
    karma: fields.ReverseRelation['UserKarma']
    class Meta:
        table = "users"

    @classmethod
    async def create_from_tg_user(cls, user: types.User):
        # if not user.id:
        #     raise UserWithoutUserIdError(
        #         f'Can\'t create user without user_id, @{user.username}'
        #     )
        user = await cls.create(
            tg_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username
        )
        
        return user 

    @classmethod
    async def get_or_create_from_tg_user(cls, user: types.User):
        try:
            if user.id:
                user = await cls.get(tg_id=user.id)
            elif user.username:
                user = await cls.get(username=user.username)
            else:
                raise DoesNotExist
        except DoesNotExist:
            user = await cls.create_from_tg_user(user=user)
        return user

    @property
    def mention_link(self):
        rez = f"<a href='tg://user?id={self.tg_id}'>{self.fullname}</a>"
        if False and self.username:
            rez += f" @{self.username}"
        return rez

    @property
    def mention_no_link(self):
        if self.username:
            rez = f"<a href='t.me/{self.username}'>{self.fullname}</a>"
        else:
            rez = self.fullname
        return rez

    def get_fullname(self):
        name = ""
        if self.first_name is not None:
            name += self.first_name
        if self.last_name is not None:
            name += f" {self.last_name}"
        if name != "":
            return name
        if self.username is not None:
            name += self.username
        elif self.tg_id is not None:
            name += "tg ID" + str(self.tg_id)
        else:
            name += f"internal ID{self.id}"
        return name

    async def get_karma(self, chat: Chat):
        user_karma =  await self.karma.filter(chat=chat).first()
        return user_karma.karma_round

    async def set_karma(self, chat: Chat, karma:int):
        user_karma =  await self.karma.filter(chat=chat).first()
        user_karma.karma = karma
        await user_karma.save()


    def __str__(self):
        rez = f"User ID {self.tg_id}, by name {self.first_name} {self.last_name}"
        if self.username:
            rez += f" with username @{self.username}"
        return rez

    def __repr__(self):
        return str(self)

    fullname = property(get_fullname)
