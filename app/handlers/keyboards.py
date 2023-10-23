from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.infrastructure.database.models import User, ModeratorEvent, KarmaEvent
from app.infrastructure.database.models.report import Report


class KarmaCancelCb(CallbackData, prefix="karma_cancel"):
    user_id: int
    karma_event_id: int
    rollback_karma: str
    moderator_event_id: int | str


class WarnCancelCb(CallbackData, prefix="warn_cancel"):
    user_id: int
    moderator_event_id: int


class ApproveReportCb(CallbackData, prefix="approve_report"):
    report_id: int
    reporter_id: int


class DeclineReportCb(CallbackData, prefix="decline_report"):
    report_id: int
    reporter_id: int


class CancelReportCb(CallbackData, prefix="cancel_report"):
    report_id: int
    reporter_id: int


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


def get_kb_warn_cancel(user: User, moderator_event: ModeratorEvent):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text='Отменить',
        callback_data=WarnCancelCb(
            user_id=user.tg_id,
            moderator_event_id=moderator_event.id_
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
                text="Подробнее",
                url="https://nometa.xyz/ru.html",
            )
        ]]
    )


def get_xy_problem_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="Подробнее",
                url="https://xyproblem.ru/",
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


def get_report_reaction_kb(user: User, report: Report) -> InlineKeyboardMarkup:
    approve = InlineKeyboardButton(
        text='Подтвердить',
        callback_data=ApproveReportCb(report_id=report.id, reporter_id=user.id).pack()
    )
    decline = InlineKeyboardButton(
        text='Отклонить',
        callback_data=DeclineReportCb(report_id=report.id, reporter_id=user.id).pack()
    )
    cancel = InlineKeyboardButton(
        text='Отменить',
        callback_data=CancelReportCb(report_id=report.id, reporter_id=user.id).pack()
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [approve, decline],
        [cancel]
    ])
