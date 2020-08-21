from aiogram import types
from aiogram.types import ContentType
from aiogram.utils.markdown import hbold
from loguru import logger

from app.misc import dp
from app.models.chat import Chat
from app.models.user import User
from app.services.change_karma import change_karma
from app.utils.exceptions import SubZeroKarma
from app.services.find_target_user import get_db_user_by_tg_user

how_change = {
    +1: 'увеличили',
    -1: 'уменьшили'
}


async def to_fast_change_karma(message: types.Message, *_, **__):
    return await message.reply("Вы слишком часто меняете карму")


@dp.message_handler(karma_change=True, has_target=True, content_types=[ContentType.STICKER, ContentType.TEXT])
@dp.throttled(to_fast_change_karma, rate=30)
async def karma_change(message: types.Message, karma: dict, user: User, chat: Chat, target: types.User):
    target_user = await get_db_user_by_tg_user(target)

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

    await message.reply(
        "Вы {how_change} карму {name} до {karma_new} ({power:+.2f})".format(
            how_change=how_change[karma['karma_change']],
            name=hbold(target_user.fullname),
            karma_new=hbold(uk.karma_round),
            power=power * karma['karma_change'],
        ),
        disable_web_page_preview=True
    )
    logger.info(
        "user {user} change karma of {target_user}",
        user=user.tg_id,
        target_user=target_user.tg_id
    )
