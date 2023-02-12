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


def get_lmgfy_kb(question: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="Подробнее",
                url=f"https://google.com/search?q={question}",
            )
        ]]
    )


def get_nometa_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="Пожалуйста не задавайте мета-вопросов в чате",
                url="https://nometa.xyz/ru.html",
            )
        ]]
    )


def get_paste_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="dpaste.org",
                url="https://dpaste.org",
            ),
            InlineKeyboardButton(
                text="gist.github.com",
                url="https://gist.github.com",
            ),
        ]]
    )
