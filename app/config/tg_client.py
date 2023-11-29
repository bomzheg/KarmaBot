from app.models.config import TgClientConfig


def load_tg_client_config(config: dict) -> TgClientConfig:
    return TgClientConfig(
        bot_token=config["bot_token"],
        request_interval=config["request_interval"],
    )
