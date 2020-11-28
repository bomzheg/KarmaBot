"""
constants, settings
"""
import os
import secrets
import typing
from datetime import timedelta
from functools import partial
from pathlib import Path

from aiogram import Bot
from dotenv import load_dotenv

from app.models.common import TypeRestriction

app_dir: Path = Path(__file__).parent.parent
load_dotenv(str(app_dir / '.env'))

PLUS = "+"
PLUS_WORDS = frozenset({
    "спасибо",
    "спс",
    "спасибочки",
    "благодарю",
    "пасиба",
    "пасеба",
    "посеба",
    "благодарочка",
    "thx",
    "мерси",
    "выручил",
})
PLUS_TRIGGERS = frozenset({PLUS, *PLUS_WORDS})
PLUS_EMOJI = frozenset({"👍", })
MINUS = "-"
MINUS_TRIGGERS = frozenset({MINUS, })
MINUS_EMOJI = frozenset({'👎', })

TIME_TO_CANCEL_ACTIONS = 60
TIME_TO_REMOVE_TEMP_MESSAGES = 30

DEFAULT_RESTRICT_DURATION = timedelta(hours=1)
FOREVER_RESTRICT_DURATION = timedelta(days=666)

# auto restrict when karma less than NEGATIVE_KARMA_TO_RESTRICT
ENABLE_AUTO_RESTRICT_ON_NEGATIVE_KARMA = bool(int(os.getenv(
    "ENABLE_AUTO_RESTRICT_ON_NEGATIVE_KARMA", default=0)))

NEGATIVE_KARMA_TO_RESTRICT = -100
KARMA_AFTER_RESTRICT = -80


class RestrictionPlanElem(typing.NamedTuple):
    duration: timedelta
    type_restriction: TypeRestriction


RESTRICTIONS_PLAN: typing.List[RestrictionPlanElem] = [
    RestrictionPlanElem(timedelta(days=7), TypeRestriction.karmic_ro),
    RestrictionPlanElem(timedelta(days=30), TypeRestriction.karmic_ro),
    RestrictionPlanElem(FOREVER_RESTRICT_DURATION, TypeRestriction.karmic_ban),
]

RO_ACTION = partial(Bot.restrict_chat_member, can_send_messages=False)
BAN_ACTION = Bot.kick_chat_member

action_for_restrict = {
    TypeRestriction.ban: BAN_ACTION,
    TypeRestriction.ro: RO_ACTION,
    TypeRestriction.karmic_ro: RO_ACTION,
    TypeRestriction.karmic_ban: BAN_ACTION,
}
COMMENT_AUTO_RESTRICT = f"Карма ниже {NEGATIVE_KARMA_TO_RESTRICT}"

PROG_NAME = "KarmaBot"
PROG_DESC = (
    "This program is a Python 3+ script. The script launches a bot in Telegram,"
    " allowing change karma for chat members"
)
PROG_EP = "© bomzheg. License WTFPL."
DESC_BETA = "Run the program in beta test mode"
DESC_POLLING = "Run tg bot with polling. Default use WebHook"

BOT_TOKEN = os.getenv("KARMA_BOT_TOKEN")
TEST_BOT_TOKEN = os.getenv("TEST_KARMA_BOT_TOKEN")
now_token: str  # in that variable setting token, that be used in this instance of bot
secret_str = secrets.token_urlsafe(16)  # for webhook path

PRINT_LOG = "print.log"

BOMZHEG_ID = 46866565
BORNTOHACK_ID = 113196531
ENTERESSI_ID = 198896585
VADIM_ID = 109601
RUD_ID = 695207573
LET45FC_ID = 384612009
STUDENT_ID = 431590221
GLOBAL_ADMIN_ID = BOMZHEG_ID
SUPERUSERS = {GLOBAL_ADMIN_ID, BOMZHEG_ID, BORNTOHACK_ID, ENTERESSI_ID, VADIM_ID,
              RUD_ID, LET45FC_ID, STUDENT_ID}
LOG_CHAT_ID = -1001404337089
DUMP_CHAT_ID = -1001459777201  # ⚙️Testing Area >>> Python Scripts

DATE_FORMAT = '%d.%m.%Y'

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", default=443)
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", default='/karmabot/')
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"

LISTEN_IP = os.getenv("LISTEN_IP", default='0.0.0.0')
LISTEN_PORT = int(os.getenv("LISTEN_PORT", default=3000))

DB_TYPE = os.getenv("DB_TYPE", default='sqlite')
LOGIN_DB = os.getenv("LOGIN_DB")
PASSWORD_DB = os.getenv("PASSWORD_DB")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_PATH = os.getenv("DB_PATH", default=app_dir / "db_data" / "karma.db")

API_ID = os.getenv("API_ID", default=6)
API_HASH = os.getenv("API_HASH", default='eb06d4abfb49dc3eeb1aeb98ae0f581e')
