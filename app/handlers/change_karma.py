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
from app.services.remove_message import remove_kb_after_sleep
from . import keyboards as kb
from ..services.adaptive_trottle import AdaptiveThrottle
from ..services.moderation import TypeRestriction
from ..utils.timedelta_functions import format_timedelta

a_throttle = AdaptiveThrottle()


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
@a_throttle.throttled(rate=30, on_throttled=too_fast_change_karma)
@dp.throttled(rate=1)
async def karma_change(message: types.Message, karma: dict, user: User, chat: Chat, target: User):

    try:
        uk, abs_change, karma_event, restrict_duration = await change_karma(
            target_user=target,
            chat=chat,
            user=user,
            how_change=karma['karma_change'],
            comment=karma['comment'],
            bot=message.bot,
        )
    except SubZeroKarma:
        return await message.reply("У Вас слишком мало кармы для этого")
    except AutoLike:
        return

    msg = await message.reply(
        "Вы {how_change} карму {name} до {karma_new} ({power:+.2f})".format(
            how_change=get_how_change_text(karma['karma_change']),
            name=hbold(target.fullname),
            karma_new=hbold(uk.karma_round),
            power=abs_change,
        ),
        disable_web_page_preview=True,
        reply_markup=kb.get_kb_karma_cancel(user, karma_event)
    )
    if restrict_duration:
        if restrict_duration == config.DURATION_AUTO_RESTRICT:
            about_next = ""
        else:
            about_next = (
                f"Вам установлена карма {config.KARMA_AFTER_RESTRICT}. "
                f"Если Ваша карма снова достигнет {config.NEGATIVE_KARMA_TO_RESTRICT} "
                f"Ваш RO будет перманентный."
            )
        await message.answer(
            "{target}, Уровень вашей кармы снизился ниже {negative_limit}. "
            "За это вы попадаете в {type_restriction} на срок {duration}!\n"
            "{about_next}".format(
                target=target.mention_link,
                negative_limit=config.NEGATIVE_KARMA_TO_RESTRICT,
                type_restriction=TypeRestriction.ro.name,
                duration=format_timedelta(restrict_duration),
                about_next=about_next,
            )
        )
    asyncio.create_task(remove_kb_after_sleep(msg, config.TIME_TO_CANCEL_ACTIONS))


@dp.callback_query_handler(kb.cb_karma_cancel.filter())
async def cancel_karma(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    if int(callback_data['user_id']) != callback_query.from_user.id:
        return await callback_query.answer("Эта кнопка не для вас", cache_time=3600)
    await cancel_karma_change(callback_data['action_id'])
    await callback_query.answer("Вы отменили изменение кармы", show_alert=True)
    await callback_query.message.delete()
