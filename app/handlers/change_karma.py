import asyncio
import typing

from aiogram import types
from aiogram.types import ContentType
from aiogram.utils.markdown import quote_html
from loguru import logger

from app.misc import dp
from app.config.main import load_config
from app.models.db import Chat, User
from app.services.change_karma import change_karma, cancel_karma_change
from app.services.settings import is_enable_karmic_restriction
from app.utils.exceptions import SubZeroKarma, CantChangeKarma, DontOffendRestricted
from app.services.remove_message import remove_kb
from . import keyboards as kb
from app.services.adaptive_trottle import AdaptiveThrottle


a_throttle = AdaptiveThrottle()
config = load_config()


def get_how_change_text(number: float) -> str:
    if number > 0:
        return "увеличили"
    if number < 0:
        return "уменьшили"
    else:
        raise ValueError("karma_trigger must be float and not 0")


async def too_fast_change_karma(message: types.Message, *_, **__):
    return await message.reply("Вы слишком часто меняете карму")


@dp.message_handler(karma_change=True, has_target=True, content_types=[
        ContentType.TEXT,

        ContentType.STICKER,

        ContentType.ANIMATION,
        ContentType.AUDIO,
        ContentType.DOCUMENT,
        ContentType.PHOTO,
        ContentType.VIDEO,
        ContentType.VOICE,
])
@a_throttle.throttled(rate=30, on_throttled=too_fast_change_karma)
@dp.throttled(rate=1)
async def karma_change(message: types.Message, karma: dict, user: User, chat: Chat, target: User):

    try:
        result_change_karma = await change_karma(
            target_user=target,
            chat=chat,
            user=user,
            how_change=karma['karma_change'],
            comment=karma['comment'],
            bot=message.bot,
        )
    except SubZeroKarma:
        return await message.reply("У Вас слишком мало кармы для этого")
    except DontOffendRestricted:
        return await message.reply("Не обижай его, он и так наказан!")
    except CantChangeKarma as e:
        logger.info("user {user} can't change karma, {e}", user=user.tg_id, e=e)
        return

    if result_change_karma.was_auto_restricted:
        notify_text = config.auto_restriction.render_auto_restriction(
            target, result_change_karma.count_auto_restrict)
    elif result_change_karma.karma_after < 0 and await is_enable_karmic_restriction(chat):
        notify_text = config.auto_restriction.render_negative_karma_notification(
            target, result_change_karma.count_auto_restrict)
    else:
        notify_text = ""

    # How match karma was changed. Sign show changed difference, not difference for cancel
    how_changed_karma = result_change_karma.user_karma.karma \
        - result_change_karma.karma_after \
        + result_change_karma.abs_change

    msg = await message.reply(
        "Вы {how_change} карму <b>{name}</b> до <b>{karma_new:.2f}</b> ({power:+.2f})"
        "\n\n{notify_text}".format(
            how_change=get_how_change_text(karma['karma_change']),
            name=quote_html(target.fullname),
            karma_new=result_change_karma.karma_after,
            power=result_change_karma.abs_change,
            notify_text=notify_text,
        ),
        disable_web_page_preview=True,
        reply_markup=kb.get_kb_karma_cancel(
            user=user,
            karma_event=result_change_karma.karma_event,
            rollback_karma=-how_changed_karma,
            moderator_event=result_change_karma.moderator_event,
        )
    )
    asyncio.create_task(remove_kb(msg, config.time_to_cancel_actions))


@dp.callback_query_handler(kb.cb_karma_cancel.filter())
async def cancel_karma(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    user_cancel_id = int(callback_data['user_id'])
    if user_cancel_id != callback_query.from_user.id:
        return await callback_query.answer("Эта кнопка не для Вас", cache_time=3600)
    karma_event_id = int(callback_data['karma_event_id'])
    rollback_karma = float(callback_data['rollback_karma'])
    moderator_event_id = callback_data['moderator_event_id']
    moderator_event_id = None if moderator_event_id == "null" else int(moderator_event_id)
    await cancel_karma_change(karma_event_id, rollback_karma, moderator_event_id, callback_query.bot)
    await callback_query.answer("Вы отменили изменение кармы", show_alert=True)
    await callback_query.message.delete()
