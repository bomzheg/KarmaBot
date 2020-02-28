# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from app import config

jobstores = {
    'default': RedisJobStore(
        jobs_key="jobs",
        run_times_key="run_times",
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB
    )
}
executors = {'default': AsyncIOExecutor()}
job_defaults = {
    'coalesce': False,
    'max_instances': 20,
    'misfire_grace_time': 3600
}
logger.info("configuring shedulder...")
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    job_defaults=job_defaults,
    executors=executors
)


async def on_startup(dispatcher: Dispatcher):
    logger.info("starting shedulder...")
    scheduler.start()


async def on_shutdown(dispatcher: Dispatcher):
    scheduler.shutdown()


def setup(executor: Executor):
    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)
