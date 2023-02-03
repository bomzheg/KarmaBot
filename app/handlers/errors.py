from aiogram import Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.types.error_event import ErrorEvent
from aiogram.utils.text_decorations import html_decoration as hd

from app.utils.exceptions import Throttled
from app.utils.log import Logger


logger = Logger(__name__)


async def errors_handler(error: ErrorEvent):
    try:
        raise error.exception
    except Throttled:
        pass
    except TelegramBadRequest as e:
        if "rights" in e.args[0] and "send" in e.args[0]:
            if error.update.message and error.update.message.chat:
                logger.info("bot are muted in chat {chat}", chat=error.update.message.chat.id)
            else:
                logger.info("bot can't send message (no rights) in update {update}", update=error.update)
            return True

    logger.exception(
        "Cause exception {e} in update {update}",
        e=error.exception, update=error.update, exc_info=error.exception
    )

    # await bot.send_message(
    #     config.log.log_chat_id,
    #     f"Получено исключение {hd.quote(error.exception)}\n"
    #     f"во время обработки апдейта {hd.quote(error.update)}\n"
    #     f"{hd.quote(error.exception.args)}"
    # )
    return True


def setup(dp: Dispatcher):
    dp.errors.register(errors_handler)
