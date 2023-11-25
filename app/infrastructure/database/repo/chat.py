from collections import namedtuple

from tortoise import BaseDBAsyncClient
from tortoise.exceptions import DoesNotExist

from app.infrastructure.database.models import UserKarma
from app.infrastructure.database.models.chat import Chat
from app.infrastructure.database.models.user import User
from app.models.db.db import karma_filters
from app.utils.exceptions import NotHaveNeighbours

TopResultEntry = namedtuple("TopResult", ("user", "karma"))
Neighbours = namedtuple("Neighbours", ("prev_id", "next_id"))


class ChatRepo:
    def __init__(self, session: BaseDBAsyncClient | None = None):
        self.session = session

    async def get_by_id(self, chat_id: int) -> Chat:
        return await Chat.get(chat_id=chat_id, using_db=self.session)

    async def save(self, chat: Chat):
        await chat.save(using_db=self.session)

    async def create_from_tg_chat(self, chat) -> Chat:
        chat = await Chat.create(
            chat_id=chat.id,
            type_=chat.type,
            title=chat.title,
            username=chat.username,
            using_db=self.session,
        )
        return chat

    async def get_or_create_from_tg_chat(self, chat) -> Chat:
        try:
            chat = await Chat.get(chat_id=chat.id)
        except DoesNotExist:
            chat = await self.create_from_tg_chat(chat=chat)
        return chat

    async def get_top_karma_list(
        self, chat: Chat, limit: int = 15
    ) -> list[TopResultEntry]:
        await chat.fetch_related("user_karma", using_db=self.session)
        users_karmas = (
            await chat.user_karma.order_by(*karma_filters)
            .limit(limit)
            .prefetch_related("user")
            .all()
        )
        rez = []
        for user_karma in users_karmas:
            user = user_karma.user
            karma = user_karma.karma_round
            rez.append(TopResultEntry(user, karma))

        return rez

    async def get_neighbours(
        self, user: User, chat: Chat
    ) -> tuple[UserKarma, UserKarma, UserKarma]:
        prev_id, next_id = await self.get_neighbours_id(chat.chat_id, user.id)
        uk = (
            await chat.user_karma.filter(user_id__in=(prev_id, next_id))
            .prefetch_related("user")
            .order_by(*karma_filters)
            .all()
        )

        user_uk = (
            await chat.user_karma.filter(user=user).prefetch_related("user").first()
        )
        return uk[0], user_uk, uk[1]

    async def get_neighbours_id(self, chat_id, user_id) -> Neighbours:
        neighbours = await self.session.execute_query(
            query="""
            SELECT prev_user_id, next_user_id
            FROM (
                SELECT
                    user_id,
                    LAG(user_id) OVER(ORDER BY karma) prev_user_id,
                    LEAD(user_id) OVER(ORDER BY karma) next_user_id
                FROM user_karma
                WHERE chat_id = ?
            )
            WHERE user_id = ?""",
            values=[chat_id, user_id],
        )
        try:
            rez = dict(neighbours[1][0])
        except IndexError:
            raise NotHaveNeighbours
        try:
            rez = int(rez["prev_user_id"]), int(rez["next_user_id"])
        except TypeError:
            raise NotHaveNeighbours
        return rez
