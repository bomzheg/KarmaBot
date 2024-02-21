from typing import Iterable

from tortoise import BaseDBAsyncClient

from app.infrastructure.database.models import Chat, KarmaEvent, User


class KarmaEventRepo:
    def __init__(self, session: BaseDBAsyncClient | None = None):
        self.session = session

    async def create(
        self,
        user_from: User,
        target: User,
        chat: Chat,
        how_change: float,
        how_change_absolute: float,
        comment: str,
    ) -> KarmaEvent:
        return await KarmaEvent.create(
            user_from=user_from,
            user_to=target,
            chat=chat,
            how_change=how_change,
            how_change_absolute=how_change_absolute,
            comment=comment[:200],
            using_db=self.session,
        )

    async def save(self, karma_event: KarmaEvent, fields: Iterable[str] | None = None):
        await karma_event.save(update_fields=fields, using_db=self.session)

    async def get_karma_event_by_id(self, karma_event_id: int) -> KarmaEvent:
        return await KarmaEvent.get(id=karma_event_id, using_db=self.session)

    async def get_last_user_karma_event(
        self, user: User, chat: Chat, limit: int = 10
    ) -> list[KarmaEvent]:
        return await (
            KarmaEvent.filter(user_to=user, chat=chat)
            .order_by("-date")
            .limit(limit)
            .prefetch_related("user_from")
            .using_db(self.session)
            .all()
        )
