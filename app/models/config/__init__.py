from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .auto_restriction import AutoRestrictionConfig
from .db import DBConfig
from .log import LogConfig
from .storage import StorageConfig
from .tg_client import TgClientConfig
from .webhook import WebhookConfig


@dataclass
class Config:
    auto_restriction: AutoRestrictionConfig
    db: DBConfig
    webhook: WebhookConfig
    app_dir: Path
    bot_token: str
    superusers: Iterable[int]
    log: LogConfig
    dump_chat_id: int
    tg_client: TgClientConfig
    storage: StorageConfig
    date_format: str = "%d.%m.%Y"
    time_to_cancel_actions: int = 60
    time_to_remove_temp_messages: int = 30
    report_karma_award: int = 0
    time_to_remove_report_karma_award_messages: int = 300  # 5 minutes. If time in seconds less than 1, then message will not be removed
    callback_query_answer_cache_time: int = 3600


__all__ = [AutoRestrictionConfig, DBConfig, LogConfig, WebhookConfig, TgClientConfig]
