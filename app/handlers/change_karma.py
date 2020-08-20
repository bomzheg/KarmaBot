from aiogram import types
from aiogram.utils.markdown import hbold
from loguru import logger
from pyrogram.errors import UsernameNotOccupied

from app.misc import dp
from app.models.chat import Chat
from app.models.user import User
from app.services.user_getter import UserGetter
from app.services.change_karma import change_karma
from app.utils.exceptions import UserWithoutUserIdError, SubZeroKarma

how_change = {
    +1: 'увеличили',
    -1: 'уменьшили'
}


def can_change_karma(target_user: User, user: User):
    return user.id != target_user.id and not target_user.is_bot


async def to_fast_change_karma(message: types.Message, *_, **__):
    return await message.reply("Вы слишком часто меняете карму")


@dp.message_handler(karma_change=True, content_types=[types.ContentType.STICKER, types.ContentType.TEXT])
@dp.throttled(to_fast_change_karma, rate=30)
async def karma_change(message: types.Message, karma: dict, user: User, chat: Chat):
    try:
        target_user = await User.get_or_create_from_tg_user(karma['user'])
    # in karma['user'] can be user with only username
    except UserWithoutUserIdError as e:
        try:
            target_user = await UserGetter.get_db_user_by_username(karma['user'].username)
        # that username can be not valid
        except (UsernameNotOccupied, IndexError):
            e.user_id = user.tg_id
            e.chat_id = chat.chat_id
            raise e
    else:
        if not can_change_karma(target_user, user):
            return logger.info("user {user} try to change self or bot karma ", user=user.tg_id)

    try:
        uk, power = await change_karma(
            target_user=target_user,
            chat=chat,
            user=user,
            how_change=karma['karma_change'],
            comment=karma['comment']
        )
    except SubZeroKarma:
        logger.info("user {user} try to change karma but have negative karma", user=user.tg_id)
        return await message.reply("У Вас слишком мало кармы для этого")

    return_text = (
        "Вы {how_change} карму "
        "{name} до {karma_new} "
        "({power:+.2f})".format(
            how_change=how_change[karma['karma_change']],
            name=hbold(target_user.fullname),
            karma_new=hbold(uk.karma_round),
            power=power * karma['karma_change'],
        )
    )
    await message.reply(return_text, disable_web_page_preview=True)
    logger.info(
        "user {user} change karma of {target_user}",
        user=user.tg_id,
        target_user=target_user.tg_id
    )
