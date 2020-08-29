from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.models import User, KarmaEvent

cb_karma_cancel = CallbackData("karma_cancel", "user_id", "action_id")


def get_kb_karma_cancel(user: User, action: KarmaEvent) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        "Отменить", callback_data=cb_karma_cancel.new(user_id=user.tg_id, action_id=action.id_)
    )]])
