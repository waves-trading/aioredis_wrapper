""""""
import asyncio
from typing import Optional
from uuid import uuid4

from .redis import RedisConnection


class LockException(Exception):
    """"""
    pass


class Lock(object):
    """"""

    def __init__(self, lock_key: str = None, lock_duration: int = 10) -> None:
        """"""

        self._lock_duration = lock_duration
        self._lock_key = lock_key if lock_key else str(uuid4())
        self._identifier = str(uuid4())

    @property
    def duration(self) -> int:
        return self._lock_duration

    @duration.setter
    def duration(self, duration: int) -> None:
        self._lock_duration = duration

    @property
    def redis_key(self) -> str:
        return self._lock_key

    @redis_key.setter
    def redis_key(self, key: str) -> None:
        self._lock_key = key

    @property
    def identifier(self) -> str:
        return self._identifier

    @identifier.setter
    def identifier(self, identifier: str) -> None:
        self._identifier = identifier

    def __str__(self):
        return f"{self.redis_key}:{self.identifier}\tfor {self.duration} seconds"


class Locker(object):
    """"""

    def __init__(self, redis_connection: RedisConnection) -> None:
        """
        :param redis_connection: async connector to redis
        """
        self._connection = redis_connection

    @staticmethod
    def create_unique_identifier(*args):
        return "/".join(args).encode().hex()

    @staticmethod
    def create_mutex_key(identifier: str):
        return f"{identifier}_mutex"

    async def lock(self, key: str = None, duration: int = 10, force: bool = False) -> Optional[Lock]:
        """"""
        lock = Lock(lock_key=key, lock_duration=duration)
        async with self._connection as conn:
            lock_result = await conn.set(
                key=lock.redis_key,
                value=lock.identifier,
                expire=lock.duration,
                exist=conn.SET_IF_NOT_EXIST if not force else None
            )
            if not lock_result:
                raise LockException("Cannot to set lock")
        return lock

    async def extend_lock(self, lock: Lock, duration: int = None) -> Optional[Lock]:
        """"""
        if duration:
            lock.duration = duration
        async with self._connection as conn:
            redis_lock_value = await conn.get(lock.redis_key)
            if not redis_lock_value:
                raise LockException("Redis key is not exists")
            if not redis_lock_value == lock.identifier:
                raise LockException("Resource is locked with another identifier")
            lock_result = await conn.expire(key=lock.redis_key, timeout=lock.duration)
            if not lock_result:
                raise LockException("Redis key is not exists")
        return lock

    async def master_use_lock(
            self,
            lock_key: str,
            max_expire_lock_time: int = 5,
            duration: int = None,
    ) -> Optional[Lock]:
        """"""
        async with self._connection as conn:
            value, ttl = await asyncio.gather(
                *[
                    conn.get(lock_key),
                    conn.ttl(lock_key)
                ]
            )

            print(f"Current lock info:\tkey: `{lock_key}`\t|value: `{value}`\t|ttl: `{ttl}`")
            if not value:
                # ttl == -2 | True
                return (
                    await self.lock(
                        key=lock_key,
                        duration=duration,
                        force=True
                    )
                )
            if ttl == -1:
                raise LockException(
                    f"Expire for key `{lock_key}` is not set."
                )
            elif ttl <= max_expire_lock_time:
                await conn.delete(
                    lock_key
                )
                return (
                    await self.lock(
                        key=lock_key,
                        duration=duration,
                        force=True
                    )
                )
            else:
                raise LockException(
                    f"Can't get mutex. ttl: `{ttl}`\tmax_expire: `{max_expire_lock_time}`."
                )
