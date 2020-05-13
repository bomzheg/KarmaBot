import os
from pathlib import Path
from dotenv import load_dotenv

app_dir: Path = Path(__file__).parent.parent
load_dotenv(str(app_dir / '.env'))

PLUS = ("+", "👍", "спасибо", "спс")
MINUS = ('-', '👎')


PROG_NAME = "KarmaBot"
PROG_DESC = (
    "This program is a Python 3+ script. The script launches a bot in Telegram,"
    " allowing change karma for chat members"
)
PROG_EP = "© bomzheg. License WTFPL."
DESC_BETA = "Run the program in beta test mode"
DESC_POLLING = "Run tg bot with polling. Default use WebHook"
os.getenv("KARMA_BOT_TOKEN")
BOT_TOKEN = os.getenv("KARMA_BOT_TOKEN")
TEST_BOT_TOKEN = os.getenv("TEST_KARMA_BOT_TOKEN")

CAPTURE_STD_ERR = False

ERR_LOG = "err.log"
PRINT_LOG = "print.log"

GLOBAL_ADMIN_ID = 46866565
BORNTOHACK = 113196531
SUPERUSERS = (GLOBAL_ADMIN_ID, BORNTOHACK)
LOG_CHAT_ID = -336404632

WEBHOOK_HOST = ''
WEBHOOK_PORT = 443
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}"
LISTEN_IP = '127.0.0.1'
LISTEN_PORT = "3001"

LOGIN_DB = os.getenv("LOGIN_DB")
PASSWORD_DB = os.getenv("PASSWORD_DB")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_TYPE = os.getenv("DB_TYPE")

REDIS_DB = int(os.getenv("REDIS_DB"))
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

