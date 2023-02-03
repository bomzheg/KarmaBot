# partially from https://github.com/aiogram/bot
import argparse

from app.models.db import db
from app.utils.executor import on_startup_webhook, on_startup_notify
from app.utils.log import Logger

import app
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
    parser = create_parser()
    namespace = parser.parse_args()

    from app import misc

    misc.setup(config)
    await db.db_init(config.db)
    await on_startup_notify(misc.bot, config)
    try:
        if namespace.polling:
            logger.info("starting polling...")

            await misc.dp.start_polling(misc.bot)
        else:
            logger.info("starting webhook...")
            await on_startup_webhook(misc.bot, config.webhook)
    finally:
        await db.on_shutdown()
