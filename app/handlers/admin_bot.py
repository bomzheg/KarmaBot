from aiogram import types
from loguru import logger

from app import config
from app.misc import bot, dp
from app.utils.log import StreamToLogger
from app.utils.send_text_file import send_log_files

_logger = StreamToLogger(logger)


@dp.message_handler(lambda message: message.chat.id == config.GLOBAL_ADMIN_ID, commands='cancel_jobs')
async def cancel_jobs(message: types.Message):
    from app.services.apscheduller import scheduler
    logger.warning("removing all jobs")
    scheduler.print_jobs(out=_logger)
    scheduler.remove_all_jobs()
    await message.reply("Данные удалены")


@dp.message_handler(is_superuser=True, commands='update_log')
async def get_log(message: types.Message):
    await send_log_files(config.LOG_CHAT_ID)


@dp.message_handler(is_superuser=True, commands='logchat')
async def get_logchat(message: types.Message):
    log_ch = (await bot.get_chat(config.LOG_CHAT_ID)).invite_link
    await bot.send_message(config.GLOBAL_ADMIN_ID, log_ch, disable_notification=True)


@dp.message_handler(is_superuser=True, commands='generate_invite_logchat')
async def generate_logchat_link(message: types.Message):
    await message.reply(await bot.export_chat_invite_link(config.LOG_CHAT_ID), disable_notification=True)


@dp.message_handler(is_superuser=True, commands='idchat')
async def get_idchat(message: types.Message):
    await message.reply(message.chat.id, disable_notification=True)


@dp.message_handler(is_superuser=True, commands=["exception"])
async def cmd_exception(message: types.Message):
    raise Exception('user press /exception')
