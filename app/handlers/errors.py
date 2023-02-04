import json
from functools import partial

from aiogram import Dispatcher, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types.error_event import ErrorEvent
from aiogram.utils.text_decorations import html_decoration as hd

from app.models.config import Config
from app.utils.exceptions import Throttled
from app.utils.log import Logger


logger = Logger(__name__)


async def errors_handler(error: ErrorEvent, bot: Bot, config: Config):
    try:
        raise error.exception
    except Throttled:
        return
    except TelegramBadRequest as e:
        if "rights" in e.message and "send" in e.message:
            if error.update.message and error.update.message.chat:
                logger.info("bot are muted in chat {chat}", chat=error.update.message.chat.id)
            else:
                logger.info("bot can't send message (no rights) in update {update}", update=error.update)
            return
    except Exception:
        pass

    logger.exception(
        "Cause exception {e} in update {update}",
        e=error.exception, update=error.update, exc_info=error.exception
    )

    await bot.send_message(
        config.log.log_chat_id,
        f"Получено исключение {hd.quote(str(error.exception))}\n"
        f"во время обработки апдейта {hd.quote(error.update.json(exclude_none=True, ensure_ascii=False))}\n"
        f"{hd.quote(json.dumps(error.exception.args))}"
    )


def setup(dp: Dispatcher, bot: Bot, config: Config):
    dp.errors.register(partial(errors_handler, bot=bot, config=config))
