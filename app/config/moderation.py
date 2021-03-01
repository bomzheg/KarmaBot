from datetime import timedelta
from functools import partial

from aiogram import Bot

from app.models.common import TypeRestriction

DEFAULT_RESTRICT_DURATION = timedelta(hours=1)
FOREVER_RESTRICT_DURATION = timedelta(days=666)
RO_ACTION = partial(Bot.restrict_chat_member, can_send_messages=False)
BAN_ACTION = Bot.kick_chat_member
action_for_restrict = {
    TypeRestriction.ban: BAN_ACTION,
    TypeRestriction.ro: RO_ACTION,
    TypeRestriction.karmic_ro: RO_ACTION,
    TypeRestriction.karmic_ban: BAN_ACTION,
}
