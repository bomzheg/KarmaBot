# partially from https://github.com/aiogram/bot
import argparse

from aiogram import Bot, Dispatcher

import app
from app.models.db import db
from app.utils.executor import on_startup_webhook, on_startup_notify
from app.utils.log import Logger
from app import middlewares
from app import handlers
from app.models.config import Config


logger = Logger(__name__)
PROGRAM_DESC = (
    "This program is a Python 3+ script. The script launches a bot in Telegram,"
    " allowing change karma for chat members"
)
PROGRAM_EP = f"{app.__copyright__} {app.__author__} License {app.__license__}."


def create_parser():
    arg_parser = argparse.ArgumentParser(prog=app.__application_name__, description=PROGRAM_DESC, epilog=PROGRAM_EP)
    arg_parser.add_argument('-p', '--polling', action='store_const', const=True,
                            help="Run tg bot with polling. Default use WebHook")
    arg_parser.add_argument('-s', '--skip-updates', action='store_const', const=True,
                            help="Skip pending updates")
    return arg_parser


async def cli(config: Config):
    bot = Bot(config.bot_token, parse_mode="HTML")
    dp = Dispatcher(storage=config.storage.create_storage())
    parser = create_parser()
    namespace = parser.parse_args()

    await db.db_init(config.db)
    logger.debug(f"As application dir using: {config.app_dir}")
    middlewares.setup(dp, config)
    logger.info("Configure handlers...")
    handlers.setup(dp)
    await on_startup_notify(bot, config)
    try:
        if namespace.polling:
            logger.info("starting polling...")
            await dp.start_polling(bot)
        else:
            logger.info("starting webhook...")
            await on_startup_webhook(bot, config.webhook)
            raise NotImplementedError("webhook are not implemented now")
    finally:
        await db.on_shutdown()
        await bot.session.close()

