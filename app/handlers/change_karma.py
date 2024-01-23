import asyncio

from aiogram import Bot, F, Router, types
from aiogram.types import ContentType, LinkPreviewOptions
from aiogram.utils.text_decorations import html_decoration as hd

from app.filters import HasTargetFilter, KarmaFilter
from app.infrastructure.database.models import Chat, ChatSettings, User
from app.infrastructure.database.repo.user import UserRepo
from app.models.config import Config
from app.services.adaptive_trottle import AdaptiveThrottle
from app.services.change_karma import cancel_karma_change, change_karma
from app.services.remove_message import remove_kb
from app.utils.exceptions import CantChangeKarma, DontOffendRestricted, SubZeroKarma
from app.utils.log import Logger

from . import keyboards as kb

logger = Logger(__name__)
router = Router(name=__name__)
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


@router.message(
    F.chat.type.in_(["group", "supergroup"]),
    HasTargetFilter(),
    KarmaFilter(),
    F.content_type.in_(
        [
            ContentType.TEXT,
            ContentType.STICKER,
            ContentType.ANIMATION,
            ContentType.AUDIO,
            ContentType.DOCUMENT,
            ContentType.PHOTO,
            ContentType.VIDEO,
            ContentType.VOICE,
        ]
    ),
)
@a_throttle.throttled(rate=30, on_throttled=too_fast_change_karma)
async def karma_change(
    message: types.Message,
    karma: dict,
    user: User,
    chat: Chat,
    chat_settings: ChatSettings,
    target: User,
    config: Config,
    bot: Bot,
    user_repo: UserRepo,
):
    try:
        result_change_karma = await change_karma(
            user=user,
            target_user=target,
            chat=chat,
            how_change=karma["karma_change"],
            is_restriction_enabled=chat_settings.karmic_restrictions,
            bot=bot,
            user_repo=user_repo,
            comment=karma["comment"],
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
            target, result_change_karma.count_auto_restrict
        )
    elif result_change_karma.karma_after < 0 and chat_settings.karmic_restrictions:
        notify_text = config.auto_restriction.render_negative_karma_notification(
            target, result_change_karma.count_auto_restrict
        )
    else:
        notify_text = ""

    # How much karma was changed. Sign show changed difference, not difference for cancel
    how_changed_karma = (
        result_change_karma.user_karma.karma
        - result_change_karma.karma_after
        + result_change_karma.abs_change
    )

    msg = await message.reply(
        "<b>{actor_name}</b>, Вы {how_change} карму <b>{target_name}</b> "
        "до <b>{karma_new:.2f}</b> ({power:+.2f})\n\n{notify_text}".format(
            actor_name=hd.quote(user.fullname),
            how_change=get_how_change_text(karma["karma_change"]),
            target_name=hd.quote(target.fullname),
            karma_new=result_change_karma.karma_after,
            power=result_change_karma.abs_change,
            notify_text=notify_text,
        ),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        allow_sending_without_reply=True,
        reply_markup=kb.get_kb_karma_cancel(
            user=user,
            karma_event=result_change_karma.karma_event,
            rollback_karma=-how_changed_karma,
            moderator_event=result_change_karma.moderator_event,
        ),
    )
    return asyncio.create_task(remove_kb(msg, config.time_to_cancel_actions))


@router.callback_query(kb.KarmaCancelCb.filter())
async def cancel_karma(
    callback_query: types.CallbackQuery,
    callback_data: kb.KarmaCancelCb,
    bot: Bot,
    user_repo: UserRepo,
):
    if callback_data.user_id != callback_query.from_user.id:
        return await callback_query.answer("Эта кнопка не для Вас", cache_time=3600)
    rollback_karma = float(callback_data.rollback_karma)
    moderator_event_id = (
        None
        if callback_data.moderator_event_id == "null"
        else callback_data.moderator_event_id
    )
    await cancel_karma_change(
        callback_data.karma_event_id, rollback_karma, moderator_event_id, bot, user_repo
    )
    await callback_query.answer("Вы отменили изменение кармы", show_alert=True)
    await callback_query.message.delete()
