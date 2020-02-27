from aiogram import types
from aiogram.utils.exceptions import BadRequest
from loguru import logger
from app import config
from app.misc import dp, bot
from app.models.chat import Chat
from app.models.user import User
from app.models.user_karma import UserKarma
from app.utils.exeptions import UserWithoutUserIdError

@dp.message_handler(commands=["top"], commands_prefix='!')
async def get_top(message: types.Message, chat: Chat):
    text_list = ""
    for user, karma in await chat.get_top_karma_list():
        text_list += f"\n{user.mention_no_link} <b>{karma}</b>"
    if text_list == "":
        text = "Никто в чате не имеет кармы"
    else:
        text = "Список самых почётных пользователей чата:" + text_list
    await message.reply(text, disable_web_page_preview=True)




how_change = {
    +1: 'увеличил',
    -1: 'уменьшил'
}

def can_change_karma(target_user: User, user: User, chat: Chat):
    if user.user_id == target_user.user_id:
        return False
    return True

@dp.message_handler(karma_change=True)
async def karma_change(message: types.Message, karma: dict, user: User, chat: Chat):
    try:
        target_user = await User.get_or_create_from_tg_user(karma['user'])
    except UserWithoutUserIdError as e:
        e.user_id = user.user_id
        e.chat_id = chat.chat_id
        logger.error(e)
        await bot.send_message(
            config.LOG_CHAT_ID, 
            f"Получено исключение {e}\n"
            "Обычно так бывает, когда бот в чате недавно и ещё не видел "
            "пользователя которому плюсанули в виде '+ @username'."
        )
        return 
    
    if not can_change_karma(target_user, user, chat):
        return
    
    uk, _ = await UserKarma.get_or_create(
        user=target_user,
        chat=chat
    )
    from_user_karma = await user.get_karma(chat)
    await uk.change(user_changed=user, how_change=karma['karma_change'])

    await message.reply(
        f"{user.mention_no_link} <b>({from_user_karma})</b> "
        f"{how_change[karma['karma_change']]} карму пользователю "
        f"{target_user.mention_no_link} <b>({uk.karma_round})</b>",
        disable_web_page_preview=True
    )

