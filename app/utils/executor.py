# partially from https://github.com/aiogram/bot
from contextlib import suppress

from aiogram import Dispatcher
from aiogram.utils.exceptions import TelegramAPIError
from aiogram.utils.executor import Executor
from loguru import logger

from app import config
from app.misc import dp
from app.models import db
from app.services import apscheduller, healthcheck, trottling

runner = Executor(dp)


async def on_startup_webhook(dispatcher: Dispatcher):
    logger.info("Configure Web-Hook URL to: {url}", url=config.WEBHOOK_URL_BASE)
    await dispatcher.bot.set_webhook(config.WEBHOOK_URL_BASE)


async def on_startup_notify(dispatcher: Dispatcher):
    with suppress(TelegramAPIError):
        await dispatcher.bot.send_message(
            chat_id=config.LOG_CHAT_ID, text="Bot started", disable_notification=True
        )
        logger.info("Notified superuser {user} about bot is started.", user=config.GLOBAL_ADMIN_ID)
    #await send_log_files(config.LOG_CHAT_ID)


def setup():
    logger.info("Configure executor...")
    db.setup(runner)
    apscheduller.setup(runner)
    healthcheck.setup(runner)
    trottling.setup(runner)
    runner.on_startup(on_startup_webhook, webhook=True, polling=False)
    runner.on_startup(on_startup_notify)
