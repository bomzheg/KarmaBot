import os

from app.models.config.webhook import WebhookConfig


def load_webhook_config() -> WebhookConfig:
    return WebhookConfig(
        host=os.getenv("WEBHOOK_HOST"),
        port=os.getenv("WEBHOOK_PORT", default=443),
        path=os.getenv("WEBHOOK_PATH", default="/karmabot/"),
        listen_host=os.getenv("LISTEN_IP", default="localhost"),
        listen_port=int(os.getenv("LISTEN_PORT", default=3000)),
    )
