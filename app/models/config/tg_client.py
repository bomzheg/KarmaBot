from dataclasses import dataclass


@dataclass
class TgClientConfig:
    bot_token: str
    api_hash: str = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
    api_id: int = 6
    request_interval: int = 100
