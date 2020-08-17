from aiogram import Dispatcher
from loguru import logger


def setup(dispatcher: Dispatcher):
    logger.info("Configure filters...")
    from .superuser import IsSuperuserFilter
    from .karma_change import KarmaFilter
    from .tg_permissions import BotHasPermissions, HasPermissions

    text_messages = [
        dispatcher.message_handlers,
        dispatcher.edited_message_handlers,
        dispatcher.callback_query_handlers,
    ]

    dispatcher.filters_factory.bind(KarmaFilter, event_handlers=text_messages)
    dispatcher.filters_factory.bind(IsSuperuserFilter, event_handlers=text_messages)
    dispatcher.filters_factory.bind(BotHasPermissions, event_handlers=text_messages)
    dispatcher.filters_factory.bind(HasPermissions, event_handlers=text_messages)
