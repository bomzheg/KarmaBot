import asyncio
import typing

from loguru import logger


class LockFactory:
    def __init__(self):
        self._locks: typing.Optional[typing.Dict[typing.Any, asyncio.Lock]] = None

    def get_lock(self, id_: typing.Any):
        if self._locks is None:
            self._locks = {}

            # Это костыль, по хорошему эта таска должна создаваться в ините,
            # для этого милваря должна создаваться после бота и диспетчера
            asyncio.create_task(self._check_and_clear())

        return self._locks.setdefault(id_, asyncio.Lock())

    def clear(self):
        if self._locks is None:
            return
        self._locks.clear()

    def clear_free(self):
        if self._locks is None:
            return
        to_remove = [key for key, lock in self._locks.items() if not lock.locked()]
        for key in to_remove:
            del self._locks[key]
            logger.debug("remove lock for {key}", key=key)

    async def _check_and_clear(self, cool_down: int = 1800):
        while True:
            await asyncio.sleep(cool_down)
            self.clear_free()
