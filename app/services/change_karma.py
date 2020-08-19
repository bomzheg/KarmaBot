from app.models import User, Chat, UserKarma, KarmaEvent


async def change_karma(user: User, target_user: User, chat: Chat, how_change: float, comment: str = ""):
    uk, power = await UserKarma.change_or_create(
        target_user=target_user,
        chat=chat,
        user_changed=user,
        how_change=how_change
    )
    await KarmaEvent(
        user_from=user,
        user_to=target_user,
        chat=chat,
        how_change=how_change,
        how_match_change=power*abs(how_change),
        coment=comment
    ).save()
    return uk, power
