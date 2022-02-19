# partially from https://github.com/aiogram/bot
import argparse

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


def cli(config: Config):

    parser = create_parser()
    namespace = parser.parse_args()

    from app import misc
    from app.utils.executor import runner

    misc.setup(config)
    if namespace.polling:
        logger.info("starting polling...")

        runner.skip_updates = namespace.skip_updates
        runner.start_polling(reset_webhook=True)
    else:
        logger.info("starting webhook...")
        runner.start_webhook(**config.webhook.listener_kwargs)
