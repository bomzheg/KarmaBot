from app.infrastructure.database.models import User, Chat, ModeratorEvent, KarmaEvent


async def get_user_info(user: User, chat: Chat, date_format: str):
    moderation_events = await ModeratorEvent.get_last_by_user(user, chat)
    karma_events = await KarmaEvent.get_last_by_user(user, chat)
    rez = [(event.date, event.format_event(date_format)) for event in [*moderation_events, *karma_events]]
    rez.sort(key=lambda t: t[0])
    return [elem[1] for elem in rez]
