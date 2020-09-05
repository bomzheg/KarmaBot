import asyncio
import typing

from aiogram import types
from aiogram.types import ContentType
from aiogram.utils.markdown import hbold

from app.misc import dp
from app import config
from app.models import Chat, User
from app.services.change_karma import change_karma, cancel_karma_change
from app.utils.exceptions import SubZeroKarma, AutoLike
from app.services.find_target_user import get_db_user_by_tg_user
from app.services.remove_message import remove_kb_after_sleep
from . import keyboards as kb


def get_how_change_text(number: float) -> str:
    if number > 0:
        return "увеличили"
    if number < 0:
        return "уменьшили"
    else:
        raise ValueError("karma_trigger must be float and not 0")


async def too_fast_change_karma(message: types.Message, *_, **__):
    return await message.reply("Вы слишком часто меняете карму")


@dp.message_handler(karma_change=True, has_target=True, content_types=[ContentType.STICKER, ContentType.TEXT])
@dp.throttled(too_fast_change_karma, rate=30)
async def karma_change(message: types.Message, karma: dict, user: User, chat: Chat, target: types.User):
    target_user = await get_db_user_by_tg_user(target)

    try:
        uk, abs_change, karma_event = await change_karma(
            target_user=target_user,
            chat=chat,
            user=user,
            how_change=karma['karma_change'],
            comment=karma['comment']
        )
    except SubZeroKarma:
        return await message.reply("У Вас слишком мало кармы для этого")
    except AutoLike:
        return

    msg = await message.reply(
        "Вы {how_change} карму {name} до {karma_new} ({power:+.2f})".format(
            how_change=get_how_change_text(karma['karma_change']),
            name=hbold(target_user.fullname),
            karma_new=hbold(uk.karma_round),
            power=abs_change,
        ),
        disable_web_page_preview=True,
        reply_markup=kb.get_kb_karma_cancel(user, karma_event)
    )
    asyncio.create_task(remove_kb_after_sleep(msg, config.TIME_TO_CANCEL_ACTIONS))


@dp.callback_query_handler(kb.cb_karma_cancel.filter())
async def cancel_karma(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    if int(callback_data['user_id']) != callback_query.from_user.id:
        return await callback_query.answer("Эта кнопка не для вас", cache_time=3600)
    await cancel_karma_change(callback_data['action_id'])
    await callback_query.answer("Вы отменили изменение кармы", show_alert=True)
    await callback_query.message.delete()
