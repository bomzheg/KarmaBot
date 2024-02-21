# partially from https://github.com/aiogram/bot
from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from app.models.config import Config, WebhookConfig
from app.utils.log import Logger

logger = Logger(__name__)


async def on_startup_webhook(bot: Bot, webhook_config: WebhookConfig):
    webhook_url = webhook_config.external_url
    logger.info("Configure Web-Hook URL to: {url}", url=webhook_url)
    await bot.set_webhook(webhook_url)


async def on_startup_notify(bot: Bot, config: Config):
    with suppress(TelegramAPIError):
        await bot.send_message(
            chat_id=config.log.log_chat_id, text="Bot started", disable_notification=True
        )
        logger.info("Notified about bot is started.")
