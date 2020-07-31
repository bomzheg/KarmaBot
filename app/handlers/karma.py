from aiogram import types
from aiogram.utils.markdown import hbold
from loguru import logger

from app.misc import dp
from app.models.chat import Chat
from app.models.user import User
from app.models.user_karma import UserKarma
from app.utils.exeptions import UserWithoutUserIdError, SubZeroKarma


@dp.message_handler(commands=["top"], commands_prefix='!')
@dp.throttled(rate=60*5)
async def get_top(message: types.Message, chat: Chat, user: User):
    args = message.get_args()
    if args:
        chat = await Chat.get(chat_id=int(args))
    logger.info("user {user} ask top karma of chat {chat}", user=user.tg_id, chat=chat.chat_id)
    text_list = ""
    for user, karma in await chat.get_top_karma_list():
        text_list += f"\n{user.mention_no_link} {hbold(karma)}"
    if text_list == "":
        text = "Никто в чате не имеет кармы"
    else:
        text = "Список самых почётных пользователей чата:" + text_list
    await message.reply(text, disable_web_page_preview=True)


@dp.message_handler(commands=["me"], commands_prefix='!')
async def get_top(message: types.Message, chat: Chat, user: User):
    args = message.get_args()
    if args:
        chat = await Chat.get(chat_id=int(args))
    logger.info("user {user} ask top karma of chat {chat}", user=user.tg_id, chat=chat.chat_id)
    uk, _ = await UserKarma.get_or_create(chat=chat, user=user)
    await message.reply(f"Ваша карма в данном чате: {uk.karma_round}", disable_web_page_preview=True)


how_change = {
    +1: 'увеличили',
    -1: 'уменьшили'
}


def can_change_karma(target_user: User, user: User):
    return user.id != target_user.id


async def to_fast_change_karma(message: types.Message, *_, **__):
    return await message.reply("Вы слишком часто меняете карму")


@dp.message_handler(karma_change=True, content_types=[types.ContentType.STICKER, types.ContentType.TEXT])
@dp.throttled(to_fast_change_karma, rate=30)
async def karma_change(message: types.Message, karma: dict, user: User, chat: Chat):
    try:
        target_user = await User.get_or_create_from_tg_user(karma['user'])
    except UserWithoutUserIdError as e:
        e.user_id = user.tg_id
        e.chat_id = chat.chat_id
        e.username = user.username
        e.text = (
            "Обычно так бывает, когда бот в чате недавно и ещё не видел "
            "пользователя, которому плюсанули в виде '+ @username'.",
        )
        raise e
    else:
        if not can_change_karma(target_user, user):
            return logger.info("user {user} try to change self karma", user=user.tg_id)

    try:
        uk, power = await UserKarma.change_or_create(
            target_user=target_user,
            chat=chat,
            user_changed=user,
            how_change=karma['karma_change']
        )
    except SubZeroKarma:
        logger.info("user {user} try to change karma but have negative karma", user=user.tg_id)
        return await message.reply("У Вас слишком мало кармы для этого")

    return_text = (
        "Вы {how_change} карму "
        "{name} до {karma_new} "
        "({power:+.1f})".format(
            how_change=how_change[karma['karma_change']],
            name=hbold(target_user.fullname),
            karma_new=hbold(uk.karma_round),
            power=power,
        )
    )
    await message.reply(return_text, disable_web_page_preview=True)
    logger.info("user {user} change karma of {target_user}", user=user.tg_id, target_user=target_user.tg_id)
