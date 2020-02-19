from aiogram import types
from loguru import logger
from app.misc import dp
from app.models.chat import Chat
from app.models.user import User
from app.models.user_karma import UserKarma

how_change = {
    +1: 'увеличил',
    -1: 'уменьшил'
}


@dp.message_handler(karma_change=True)
async def karma_change(message: types.Message, karma: dict, user: User, chat: Chat):
    target_user = await User.get_or_create_from_tg_user(karma['user'])
    uk, _ = await UserKarma.get_or_create(
        user=target_user,
        chat=chat
    )

    if karma['karma_change'] > 0:
        await uk.up(user_changed=user)
    elif karma['karma_change'] < 0:
        await uk.down(user_changed=user)

    await message.reply(
        f"{await user.get_small_card_no_link()} "
        f"{how_change[karma['karma_change']]} карму пользователю "
        f"{await target_user.get_small_card_no_link()} ({uk.karma_round})",
        disable_web_page_preview=True
    )
