from aiogram import types
from aiogram.utils.markdown import hlink, quote_html
from pyrogram.errors import RPCError
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

from .chat import Chat
from app.services.user_getter import user_getter


class User(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.BigIntField(unique=True, null=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=32, null=True)
    is_bot: bool = fields.BooleanField(null=True)
    # noinspection PyUnresolvedReferences
    karma: fields.ReverseRelation['UserKarma']

    class Meta:
        table = "users"
        unique = 'tg_id'

    @classmethod
    async def create_from_tg_user(cls, user: types.User):
        user = await cls.create(
            tg_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_bot=user.is_bot
        )

        return user

    async def update_user_data(self, user_tg):
        # TODO изучить фреймворк лучше - уверен есть встроенная функция для обновления только в случае расхождений
        changed = False

        if self.tg_id is None and user_tg.id is not None:
            changed = True
            self.tg_id = user_tg.id

        if user_tg.first_name is not None:
            if self.first_name != user_tg.first_name:
                changed = True
                self.first_name = user_tg.first_name

            if self.last_name != user_tg.last_name:
                changed = True
                self.last_name = user_tg.last_name

            if self.username != user_tg.username:
                changed = True
                self.username = user_tg.username
            if self.is_bot is None and user_tg.is_bot is not None:
                changed = True
                self.is_bot = user_tg.is_bot

        if changed:
            await self.save()

    @classmethod
    async def get_or_create_from_tg_user(cls, user_tg: types.User):
        if user_tg.id is None:
            try:
                user_tg = await user_getter.get_user(user_tg.username)
            except RPCError:
                user = await cls.get_or_create_by_username(user_tg.username)
            else:
                user, _ = await cls.get_or_create(tg_id=user_tg.id)
                await user.update_user_data(user_tg)
            return user

        try:
            try:
                user = await cls.get(tg_id=user_tg.id)
            except DoesNotExist:
                # искать в бд по юзернейму нужно на тот случай, что юзер уже импортирован
                if user_tg.username:
                    user = await cls.get(username=user_tg.username, tg_id__isnull=True)
                else:
                    raise DoesNotExist

        except DoesNotExist:
            return await cls.create_from_tg_user(user=user_tg)
        else:
            await user.update_user_data(user_tg)
            return user

    @classmethod
    async def get_or_create_by_username(cls, username: str):
        try:
            user = await cls.get(username=username)
        except DoesNotExist:
            user_tg = await user_getter.get_user(username)
            user = await cls.get_or_create_from_tg_user(user_tg)
        return user

    @property
    def mention_link(self):
        return hlink(self.fullname, f"tg://user?id={self.tg_id}")

    @property
    def mention_no_link(self):
        if self.username:
            rez = hlink(self.fullname, f"t.me/{self.username}")
        else:
            rez = quote_html(self.fullname)
        return rez

    @property
    def fullname(self):
        if self.last_name is not None:
            return ' '.join((self.first_name, self.last_name))
        return self.first_name or self.username or self.tg_id or self.id

    async def get_karma(self, chat: Chat):
        user_karma = await self.karma.filter(chat=chat).first()
        # noinspection PyUnresolvedReferences
        return user_karma.karma_round

    async def set_karma(self, chat: Chat, karma: int):
        user_karma = await self.karma.filter(chat=chat).first()
        user_karma.karma = karma
        await user_karma.save()

    def __str__(self):
        rez = f"User ID {self.tg_id}, by name {self.first_name} {self.last_name}"
        if self.username:
            rez += f" with username @{self.username}"
        return rez

    def __repr__(self):
        return str(self)

