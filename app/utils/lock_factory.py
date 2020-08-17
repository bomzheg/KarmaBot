import asyncio
import typing

from loguru import logger


class LockFactory:
    def __init__(self):
        self._locks: typing.Optional[typing.Dict[typing.Any, asyncio.Lock]] = None

    def get_lock(self, id_: typing.Any):
        if self._locks is None:
            self._locks = {}
            asyncio.create_task(self._check_and_clear())
        return self._locks.setdefault(id_, asyncio.Lock())

    def clear(self):
        if self._locks is None:
            return
        self._locks.clear()

    def clear_free(self):
        if self._locks is None:
            return
        for key, lock in self._locks.items():
            if not lock.locked():
                self._locks.pop(key)
                logger.debug("remove lock for {key}", key=key)

    async def _check_and_clear(self, cool_down: int = 1800):
        while True:
            await asyncio.sleep(cool_down)
            self.clear_free()
