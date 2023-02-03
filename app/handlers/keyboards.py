from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.models.db import User, KarmaEvent, ModeratorEvent


class KarmaCancelCb(CallbackData, prefix="karma_cancel"):
    user_id: int
    karma_event_id: int
    rollback_karma: str
    moderator_event_id: int | str


def get_kb_karma_cancel(
        user: User, karma_event: KarmaEvent, rollback_karma: float, moderator_event: ModeratorEvent
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="Отменить",
        callback_data=KarmaCancelCb(
            user_id=user.tg_id,
            karma_event_id=karma_event.id_,
            rollback_karma=f"{rollback_karma:.2f}",
            moderator_event_id=moderator_event.id_ if moderator_event is not None else "null",
        ).pack()
    )]])
