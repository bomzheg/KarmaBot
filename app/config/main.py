import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

from app.models.config import Config, TgClientConfig

from .db import load_db_config
from .karmic_restriction import load_karmic_restriction_config
from .log import load_log_config
from .logging_config import logging_setup
from .storage import load_storage
from .webhook import load_webhook_config


@lru_cache
def load_config(config_dir: Path = None) -> Config:
    app_dir: Path = Path(__file__).parent.parent.parent
    config_dir = config_dir or app_dir / "config"

    with (config_dir / "bot-config.yaml").open("r", encoding="utf-8") as f:
        config_file_data = yaml.load(f, Loader=yaml.FullLoader)

    log_config = load_log_config(
        app_dir=app_dir, log_chat_id=config_file_data["log_chat_id"]
    )
    logging_setup(config_dir, log_config)

    load_dotenv(str(config_dir / ".env"))
    _bot_token = os.getenv("KARMA_BOT_TOKEN")

    return Config(
        auto_restriction=load_karmic_restriction_config(),
        db=load_db_config(app_dir),
        webhook=load_webhook_config(),
        app_dir=app_dir,
        bot_token=_bot_token,
        superusers=frozenset(config_file_data["superusers"]),
        log=log_config,
        dump_chat_id=config_file_data["dump_chat_id"],
        tg_client=TgClientConfig(bot_token=_bot_token),
        storage=load_storage(config_file_data["storage"]),
        report_karma_award=config_file_data.get("report_karma_award", 0),
        time_to_remove_report_karma_award_messages=config_file_data.get(
            "time_to_remove_report_karma_award_messages", 300
        ),
        callback_query_answer_cache_time=config_file_data.get(
            "callback_query_answer_cache_time", 3600
        ),
    )
