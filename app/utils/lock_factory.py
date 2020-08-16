import asyncio
import typing


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

    async def _check_and_clear(self, cool_down: int = 3600):
        while True:
            self.clear_free()
            await asyncio.sleep(cool_down)
