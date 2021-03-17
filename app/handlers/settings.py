from aiogram import types

from app.misc import dp
from app.models import Chat
from app.services.settings import enable_karmic_restriction, disable_karmic_restriction


@dp.message_handler(commands="enable_karmic_ro", user_can_restrict_members=True, commands_prefix='!')
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


@dp.message_handler(commands="disable_karmic_ro", user_can_restrict_members=True, commands_prefix='!')
async def disable_karmic_ro_cmd(message: types.Message, chat: Chat):
    await disable_karmic_restriction(chat)
    await message.reply("Кармобаны отключены")
