from aiogram import types
from aiogram.utils.exceptions import CantParseEntities
from aiogram.utils.markdown import quote_html
from loguru import logger

from app.config.main import load_config
from app.misc import dp, bot


config = load_config()


@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    try:
        raise exception
    except CantParseEntities as e:
        logger.error("Cause exception {e} in update {update}", e=e, update=update)

    except Exception as e:
        logger.exception("Cause exception {e} in update {update}", e=e, update=update)

    await bot.send_message(
        config.log.log_chat_id,
        f"Получено исключение {quote_html(exception)}\n"
        f"во время обработки апдейта {quote_html(update)}\n"
        f"{quote_html(exception.args)}"
    )
    return True
