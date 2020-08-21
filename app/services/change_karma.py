from loguru import logger

from app.models import User, Chat, UserKarma, KarmaEvent
from app.utils.exceptions import AutoLike


def can_change_karma(target_user: User, user: User):
    return user.id != target_user.id and not target_user.is_bot


async def change_karma(user: User, target_user: User, chat: Chat, how_change: float, comment: str = ""):
    if not can_change_karma(target_user, user):
        logger.info("user {user} try to change self or bot karma ", user=user.tg_id)
        raise AutoLike(user_id=user.tg_id, chat_id=chat.chat_id)

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
        comment=comment
    ).save()
    return uk, power
