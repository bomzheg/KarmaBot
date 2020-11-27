from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.models import User, KarmaEvent, ModeratorEvent

cb_karma_cancel = CallbackData("karma_cancel", "user_id", "karma_event_id", "rollback_karma", "moderator_event_id")


def get_kb_karma_cancel(
        user: User, karma_event: KarmaEvent, rollback_karma: float, moderator_event: ModeratorEvent
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        "Отменить", callback_data=cb_karma_cancel.new(
            user_id=user.tg_id,
            karma_event_id=karma_event.id_,
            rollback_karma=f"{rollback_karma:.2f}",
            moderator_event_id=moderator_event.id_ if moderator_event is not None else "null",
        )
    )]])
