from aiogram import types

from app.misc import dp
from app.models.db import Chat
from app.services.settings import enable_karmic_restriction, disable_karmic_restriction, get_settings_card, \
    enable_karma_counting, disable_karma_counting


@dp.message_handler(commands="settings", commands_prefix="!/")
async def get_settings(message: types.Message, chat: Chat):
    settings_card = await get_settings_card(chat)
    await message.answer(settings_card)


@dp.message_handler(
    commands="enable_karmic_ro",
    user_can_restrict_members=True,
    commands_prefix='!/',
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


@dp.message_handler(
    commands="disable_karmic_ro",
    user_can_restrict_members=True,
    commands_prefix='!/',
)
async def disable_karmic_ro_cmd(message: types.Message, chat: Chat):
    await disable_karmic_restriction(chat)
    await message.reply("Кармобаны отключены")


@dp.message_handler(
    commands="enable_karma",
    user_can_delete_messages=True,
    commands_prefix='!/',
)
async def enable_karma(message: types.Message, chat: Chat):
    await enable_karma_counting(chat)
    await message.reply(
        "Включён подсчёт кармы"
    )


@dp.message_handler(
    commands="disable_karma",
    user_can_delete_messages=True,
    commands_prefix='!/',
)
async def disable_karma(message: types.Message, chat: Chat):
    await disable_karma_counting(chat)
    await message.reply(
        "Выключен подсчёт кармы"
    )
