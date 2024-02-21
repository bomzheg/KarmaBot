from app.infrastructure.database.models import Chat, ModeratorEvent, User
from app.infrastructure.database.repo.karma_event import KarmaEventRepo


async def get_user_info(karma_event_repo: KarmaEventRepo, user: User, chat: Chat, date_format: str):
    moderation_events = await ModeratorEvent.get_last_by_user(user, chat)
    karma_events = await karma_event_repo.get_last_user_karma_event(user, chat)
    rez = [
        (event.date, event.format_event(date_format))
        for event in [*moderation_events, *karma_events]
    ]
    rez.sort(key=lambda t: t[0])
    return [elem[1] for elem in rez]
