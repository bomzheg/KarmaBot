import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

from app.models.config import Config, TgClientConfig
from .db import load_db_config
from .karmic_restriction import load_karmic_restriction_config
from .log import load_log_config
from .webhook import load_webhook_config
from .logging_config import logging_setup


@lru_cache
def load_config(config_dir: Path = None) -> Config:
    app_dir: Path = Path(__file__).parent.parent.parent
    config_dir = config_dir or app_dir / 'config'
    load_dotenv(str(config_dir / '.env'))
    log_config = load_log_config(app_dir=app_dir)
    logging_setup(config_dir, log_config)

    _bot_token = os.getenv("KARMA_BOT_TOKEN")
    with (config_dir / "bot-config.yml").open('r', encoding="utf-8") as f:
        config_file_data = yaml.load(f, Loader=yaml.FullLoader)

    return Config(
        auto_restriction=load_karmic_restriction_config(),
        db=load_db_config(app_dir),
        webhook=load_webhook_config(),
        app_dir=app_dir,
        bot_token=_bot_token,
        superusers=frozenset(config_file_data['superusers']),
        log=log_config,
        dump_chat_id=-1001459777201,  # ⚙️Testing Area >>> Python Scripts,
        tg_client=TgClientConfig(bot_token=_bot_token),
    )
