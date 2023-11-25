from datetime import datetime

from aiogram import types
from tortoise import BaseDBAsyncClient
from tortoise.exceptions import DoesNotExist

from app.infrastructure.database.models import Chat, User
from app.models import dto
from app.models.common import TypeRestriction
from app.utils.exceptions import UserWithoutUserIdError


class UserRepo:
    def __init__(self, session: BaseDBAsyncClient | None = None):
        self.session = session

    async def get_by_id(self, user_id: int) -> User:
        return await User.get(id=user_id, using_db=self.session)

    async def save(self, user: User):
        await user.save(using_db=self.session)

    async def create_from_tg_user(self, user: types.User) -> User:
        user = await User.create(
            tg_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_bot=user.is_bot,
            using_db=self.session,
        )

        return user

    async def update_user_data(self, user: User, tg_user: types.User):
        changed = False

        if user.tg_id is None and tg_user.id is not None:
            changed = True
            user.tg_id = tg_user.id

        if tg_user.first_name is not None:
            if user.first_name != tg_user.first_name:
                changed = True
                user.first_name = tg_user.first_name

            if user.last_name != tg_user.last_name:
                changed = True
                user.last_name = tg_user.last_name

            if user.username != tg_user.username:
                changed = True
                user.username = tg_user.username
            if user.is_bot is None and tg_user.is_bot is not None:
                changed = True
                user.is_bot = tg_user.is_bot

        if changed:
            await self.save(user)

    async def get_or_create_from_tg_user(
        self, tg_user: types.User | dto.TargetUser
    ) -> User:
        if tg_user.id is None:
            try:
                return await User.get(username__iexact=tg_user.username)
            except DoesNotExist:
                raise UserWithoutUserIdError(username=tg_user.username)

        try:
            user = await User.get(tg_id=tg_user.id)
        except DoesNotExist:
            return await self.create_from_tg_user(user=tg_user)
        else:
            await user.update_user_data(tg_user)

        return user

    async def get_karma(self, user: User, chat: Chat) -> float | None:
        user_karma = await user.karma.filter(chat=chat).using_db(self.session).first()
        if user_karma:
            return user_karma.karma_round
        return None

    async def set_karma(self, user: User, chat: Chat, karma: int):
        user_karma = await user.karma.filter(chat=chat).using_db(self.session).first()
        user_karma.karma = karma
        await user_karma.save(using_db=self.session)

    async def get_number_in_top_karma(self, user: User, chat: Chat) -> int:
        user_karma = await user.karma.filter(chat=chat).using_db(self.session).first()
        return await user_karma.filter(
            chat_id=user_karma.chat_id, karma__gte=user_karma.karma
        ).count()

    async def is_read_only(self, user: User, chat: Chat) -> bool:
        user_restrictions = (
            await user.my_restriction_events.filter(
                chat=chat, type_restriction=TypeRestriction.ro.name
            )
            .using_db(self.session)
            .all()
        )

        for restriction in user_restrictions:
            if (
                restriction.timedelta_restriction
                and restriction.date + restriction.timedelta_restriction
                > datetime.now()
            ):
                return True
        return False
