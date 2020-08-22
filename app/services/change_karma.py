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
    ke = KarmaEvent(
        user_from=user,
        user_to=target_user,
        chat=chat,
        how_change=how_change,
        how_change_absolute=power*how_change,
        comment=comment
    )
    await ke.save()
    logger.info(
        "user {user} change karma of {target_user} in chat {chat}",
        user=user.tg_id,
        target_user=target_user.tg_id,
        chat=chat.chat_id
    )
    return uk, power, ke


async def cancel_karma_change(karma_event_id):
    karma_event = await KarmaEvent.get(id_=karma_event_id)

    # noinspection PyUnresolvedReferences
    user_to_id = karma_event.user_to_id
    # noinspection PyUnresolvedReferences
    user_from_id = karma_event.user_from_id
    # noinspection PyUnresolvedReferences
    chat_id = karma_event.chat_id

    user_karma = await UserKarma.get(chat_id=chat_id, user_id=user_to_id)
    user_karma.karma -= karma_event.how_change_absolute
    await user_karma.save(update_fields=['karma'])
    await karma_event.delete()
    logger.info(
        "user {user} cancel change karma to user {target} in chat {chat}",
        user=user_from_id, target=user_to_id, chat=chat_id)
