import asyncio
import typing


class LockFactory:
    def __init__(self):
        self._locks: typing.Optional[typing.Dict[typing.Any, asyncio.Lock]] = None

    def get_lock(self, id_: typing.Any):
        if self._locks is None:
            self._locks = {}
        return self._locks.setdefault(id_, asyncio.Lock())

    def clear(self):
        if self._locks is None:
            return
        self._locks.clear()
