from aiogram import types
from loguru import logger

from app import config
from app.misc import dp, bot


@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    try:
        raise exception
    except Exception as e:
        logger.exception("Cause exception {e} in update {update}", e=e, update=update)
        await bot.send_message(config.LOG_CHAT_ID, f"Получено исключение {e}\n"
                                                   f"во время обработки апдейта {update}")
    return True
