from aiogram import types
from aiogram.utils.exceptions import CantParseEntities, BadRequest
from aiogram.utils.markdown import quote_html

from app.config.main import load_config
from app.misc import dp, bot
from app.utils.log import Logger


logger = Logger(__name__)


@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    try:
        raise exception
    except CantParseEntities as e:
        logger.error("Cause exception {e} in update {update}", e=e, update=update)
        return True
    except BadRequest as e:
        if "rights" in e.args[0] and "send" in e.args[0]:
            if update.message and update.message.chat:
                logger.info("bot are muted in chat {chat}", chat=update.message.chat.id)
            else:
                logger.info("bot can't send message (no rights) in update {update}", update=update)
            return True

    logger.exception(
        "Cause exception {e} in update {update}",
        e=exception, update=update, exc_info=exception
    )

    await bot.send_message(
        load_config().log.log_chat_id,
        f"Получено исключение {quote_html(exception)}\n"
        f"во время обработки апдейта {quote_html(update)}\n"
        f"{quote_html(exception.args)}"
    )
    return True
