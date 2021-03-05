# partially from https://github.com/aiogram/bot
import argparse
import functools

from loguru import logger

from app.models.config import WebhookConfig, Config

try:
    import aiohttp_autoreload
except ImportError:
    aiohttp_autoreload = None


PROG_NAME = "KarmaBot"
PROG_DESC = (
    "This program is a Python 3+ script. The script launches a bot in Telegram,"
    " allowing change karma for chat members"
)
PROG_EP = "© bomzheg. License WTFPL."


def create_parser():
    arg_parser = argparse.ArgumentParser(prog=PROG_NAME, description=PROG_DESC, epilog=PROG_EP)
    arg_parser.add_argument('-p', '--polling', action='store_const', const=True,
                            help="Run tg bot with polling. Default use WebHook")
    arg_parser.add_argument('-a', '--autoreload', action='store_const', const=True,
                            help="Reload application on file changes")
    arg_parser.add_argument('-s', '--skip-updates', action='store_const', const=True,
                            help="Skip pending updates")
    return arg_parser


def cli(config: Config):
    def auto_reload_mixin(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if namespace.autoreload and aiohttp_autoreload:
                logger.warning(
                    "Application started in live-reload mode. Please disable it in production!"
                )
                aiohttp_autoreload.start()
            elif namespace.autoreload and not aiohttp_autoreload:
                logger.warning("`aiohttp_autoreload` is not installed.", err=True)
            return func(*args, **kwargs)

        return wrapper

    @auto_reload_mixin
    def polling(skip_updates: bool):
        """
        Start application
        """
        from app.utils.executor import runner
        logger.info("starting polling...")

        runner.skip_updates = skip_updates
        runner.start_polling(reset_webhook=True)

    @auto_reload_mixin
    def webhook(webhook_config: WebhookConfig):
        """
        Run application in webhook mode
        """
        from app.utils.executor import runner
        logger.info("starting webhook...")
        runner.start_webhook(**webhook_config.listener_kwargs)

    parser = create_parser()
    namespace = parser.parse_args()

    from app.utils import log
    from app import misc

    log.setup(config.log)
    misc.setup(config)
    if namespace.polling:
        polling(namespace.skip_updates)
    else:
        webhook(config.webhook)
