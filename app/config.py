PROG_NAME = "KarmaBot"
PROG_DESC = (
    "This program is a Python 3+ script. The script launches a bot in Telegram,"
    " allowing change karma for chat members"
)
PROG_EP = "© bomzheg. License WTFPL."
DESC_BETA = "Run the program in beta test mode"
DESC_POLLING = "Run tg bot with polling. Default use WebHook"

BOT_TOKEN = ""
TEST_BOT_TOKEN = ""

ERR_LOG = "err.log"
PRINT_LOG = "print.log"

GLOBAL_ADMIN_ID = 0
SUPERUSERS = [GLOBAL_ADMIN_ID]
LOG_CHAT_ID = -0

WEBHOOK_HOST = ''
WEBHOOK_PORT = 443
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}"
WEBHOOK_SSL_CERT = f'/etc/letsencrypt/live/{WEBHOOK_HOST}/cert.pem'
LISTEN_IP = '127.0.0.1'
LISTEN_PORT = "3001"

LOGIN_DB = ""
PASSWORD_DB = ""
DB_NAME = ""
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_TYPE = 'mysql'

REDIS_DB = 13
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
