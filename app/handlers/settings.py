from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.text_decorations import html_decoration as hd

from app.filters import HasPermissions
from app.filters.basic_arguments import single_non_negative_int
from app.infrastructure.database.models import Chat, ChatSettings
from app.services.settings import (
    disable_karma_counting,
    disable_karmic_restriction,
    enable_karma_counting,
    enable_karmic_restriction,
    get_settings_card,
    update_report_reward,
)

router = Router(name=__name__)


@router.message(Command(commands="settings", prefix="!/"))
async def get_settings(message: types.Message, chat: Chat):
    settings_card = await get_settings_card(chat)
    await message.answer(settings_card)


@router.message(
    Command("enable_karmic_ro", prefix="!/"),
    HasPermissions(can_restrict_members=True),
)
async def enable_karmic_ro_cmd(message: types.Message, chat: Chat):
    await enable_karmic_restriction(chat)
    await message.reply(
        "<b>Кармобаны</b>\n\n"
        "Было включено правило кармобанов:\n"
        "Пользователь, чья карма достигнет -100 получит RO (read only) на неделю. "
        "При этом его карма будет повышена до -80.\n"
        "Если такой пользователь допустит повторного снижения кармы до -100 "
        "он получит RO на месяц и его карма будет снова возвращена на отметку -80.\n"
        "В третий раз - будет вечный бан.\n"
    )


@router.message(
    Command("disable_karmic_ro", prefix="!/"),
    HasPermissions(can_restrict_members=True),
)
async def disable_karmic_ro_cmd(message: types.Message, chat: Chat):
    await disable_karmic_restriction(chat)
    await message.reply("Кармобаны отключены")


@router.message(
    Command("enable_karma", prefix="!/"),
    HasPermissions(can_delete_messages=True),
)
async def enable_karma(message: types.Message, chat: Chat):
    await enable_karma_counting(chat)
    await message.reply("Включён подсчёт кармы")


@router.message(
    Command("disable_karma", prefix="!/"),
    HasPermissions(can_delete_messages=True),
)
async def disable_karma(message: types.Message, chat: Chat):
    await disable_karma_counting(chat)
    await message.reply("Выключен подсчёт кармы")


@router.message(
    Command("set_report_reward", prefix="!/"),
    HasPermissions(can_delete_messages=True),
    single_non_negative_int,
)
async def set_report_reward(
    message: types.Message, chat_settings: ChatSettings, value: int
):
    await update_report_reward(chat_settings, value)
    if value != 0:
        reply_text = f"Награда за принятый репорт обновлена: +{value} кармы."
    else:
        reply_text = "Награды за репорт выключены."

    if not chat_settings.karma_counting and value != 0:
        reply_text += hd.bold(
            "\n\nЧтобы награды за репорт работали, необходимо включить подсчёт кармы в чате"
        )

    await message.reply(reply_text)


@router.message(
    Command("set_report_reward", prefix="!/"),
    HasPermissions(can_delete_messages=True),
)
async def set_report_reward_invalid_arg(message: types.Message):
    await message.reply(
        f"Неверный аргумент команды. Введите неотрицательное число.\n"
        f"Например {hd.code('/set_report_reward 20')}\n\n"
        f"Чтобы выключить награды, нужно ввести 0:\n"
        f"{hd.code('/set_report_reward 0')}"
    )
