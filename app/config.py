import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

app_dir: Path = Path(__file__).parent.parent
load_dotenv(str(app_dir / '.env'))

PLUS = ("+",  "спасибо", "спс")
PLUS_EMOJI = ("👍", )
MINUS = ('-', )
MINUS_EMOJI = ('👎', )


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
now_token: str
secret_str = secrets.token_urlsafe(16)

CAPTURE_STD_ERR = True

ERR_LOG = "err.log"
PRINT_LOG = "print.log"

BOMZHEG_ID = 46866565
BORNTOHACK_ID = 113196531
ENTERESSI_ID = 198896585
VADIM_ID = 109601
RUD_ID = 695207573
LET45FC_ID = 384612009
STUDENT_ID = 431590221
GLOBAL_ADMIN_ID = BOMZHEG_ID
SUPERUSERS = tuple({GLOBAL_ADMIN_ID, BOMZHEG_ID, BORNTOHACK_ID, ENTERESSI_ID, VADIM_ID,
                    RUD_ID, LET45FC_ID, STUDENT_ID})
LOG_CHAT_ID = -336404632
DUMP_CHAT_ID = -1001459777201  # Fucin' Testing Area

DEBUG_MODE = os.getenv("DEBUG_MODE")

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", default=443)
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", default='karmabot')
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"

LISTEN_IP = os.getenv("LISTEN_IP", default='0.0.0.0')
LISTEN_PORT = int(os.getenv("LISTEN_PORT", default=3000))

DB_TYPE = os.getenv("DB_TYPE", default='sqlite')
LOGIN_DB = os.getenv("LOGIN_DB")
PASSWORD_DB = os.getenv("PASSWORD_DB")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_PATH = os.getenv("DB_PATH", default=str(app_dir / 'karma.db'))

REDIS_DB = int(os.getenv("REDIS_DB"))
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

