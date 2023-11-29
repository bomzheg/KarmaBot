# from https://gist.github.com/jorektheglitch/5ea4972d9cb87c2ec682604e53d1ff94 by @entressi
import asyncio
import logging
from asyncio import Task

logger = logging.getLogger(__name__)


class RestrictCall:
    def __init__(self, delay):
        self.delay = delay
        self.queue = asyncio.Queue()
        self.bg_worker: Task | None = None

    def start_worker(self):
        self.bg_worker = asyncio.create_task(self.queue_processor())

    def stop_worker(self):
        self.bg_worker.cancel()

    async def queue_processor(self):
        while True:
            logger.debug("Worker is waiting for events")
            can_go = await self.queue.get()
            can_go.set()
            logger.debug("Worker fired event, sleeping for %s seconds", self.delay)
            await asyncio.sleep(self.delay)

    def __call__(self, func):
        async def wrapped(*args, **kwargs):
            can_go = asyncio.Event()
            logger.debug("Invoking restricted function")
            await self.queue.put(can_go)
            logger.debug("Waiting for the queue")
            await can_go.wait()
            logger.debug("Calling restricted function")
            return await func(*args, **kwargs)

        return wrapped
