# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from aiohttp_healthcheck import HealthCheck
from loguru import logger

from app import config

health = HealthCheck()


def setup(executor: Executor):
    logger.info("Configure helthcheck")
    executor.on_startup(on_startup, webhook=True, polling=False)


async def on_startup(dispatcher: Dispatcher):
    from app.utils.executor import runner

    logger.info("Setup healthcheck")

    health.add_check(check_redis)
    health.add_check(check_mysql)
    health.add_check(check_webhook)
    runner.web_app.router.add_get("/healthcheck", health)


async def check_redis():
    from app.misc import storage

    try:
        redis = await storage.redis()
        info = await redis.info()
    except Exception as e:
        return False, str(e)
    return True, f"Redis {info['server']['redis_version']}"


async def check_mysql():
    from tortoise.transactions import in_transaction

    try:
        async with in_transaction() as conn:
            version = await conn.execute_query("select version();")
    except Exception as e:
        return False, str(e)
    return True, version


async def check_webhook():
    from app.misc import bot

    webhook = await bot.get_webhook_info()
    if webhook.url and webhook.url == config.WEBHOOK_URL_BASE:
        return True, f"Webhook configured. Pending updates count {webhook.pending_update_count}"
    else:
        logger.error("Configured wrong webhook URL {webhook}", webhook=webhook.url)
        return False, "Configured invalid webhook URL"
