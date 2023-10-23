from tortoise import Tortoise, run_async

from app.models.config import DBConfig
from app.utils.log import Logger


logger = Logger(__name__)
__models__ = ['app.infrastructure.database.models']
karma_filters = ("-karma", "uc_id")


async def db_init(db_config: DBConfig):
    db_url = db_config.create_url_config()
    logger.info("connecting to db {db_url}", db_url=db_url)
    await Tortoise.init(
        db_url=db_url,
        modules={'models': __models__}
    )


async def on_shutdown():
    await Tortoise.close_connections()


async def generate_schemas_db(db_config: DBConfig):
    await db_init(db_config)
    await Tortoise.generate_schemas()


def generate_schemas(db_config: DBConfig):
    run_async(generate_schemas_db(db_config))



"""
CREATE TABLE "reports" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "created_time" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "resolution_time" TIMESTAMP,
    "reported_message_id" BIGINT NOT NULL,
    "reported_message_content" VARCHAR(4096) NOT NULL,
    "status" VARCHAR(9) NOT NULL  /* approved: Approved\ndeclined: Declined\npending: Pending\ncancelled: Cancelled */,
    "chat_id" BIGINT NOT NULL REFERENCES "chats" ("chat_id") ON DELETE CASCADE,
    "reported_user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "reporter_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "resolved_by_id" INT REFERENCES "users" ("id") ON DELETE CASCADE
)
"""
