""""""
import asyncio
import hashlib
from typing import Optional
from uuid import uuid4
from aioredis import Redis


# from .redis import RedisConnection


class BaseLockException(Exception):
    pass


class LockException(BaseLockException):
    """"""
    pass


class ReleaseLockException(BaseLockException):
    """"""
    pass


class Lock(object):
    """"""

    def __init__(
            self,
            lock_key: str = None,
            lock_duration: float = 10.0,
            priority_mode: bool = False,
            identifier: str = None
    ) -> None:
        """"""
        self._lock_duration = lock_duration
        self._lock_key = lock_key if lock_key else str(uuid4())
        self._priority_mode = priority_mode
        self._identifier = identifier if identifier else str(uuid4())

    @property
    def duration(self) -> float:
        return self._lock_duration

    @duration.setter
    def duration(self, duration: float) -> None:
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

    @property
    def priority_mode(self) -> bool:
        return self._priority_mode

    @priority_mode.setter
    def priority_mode(self, priority_mode: bool) -> None:
        self._priority_mode = priority_mode

    def __str__(self):
        return f"{self.redis_key}:{self.identifier}\t:{self.priority_mode} for {self.duration} seconds"


class Locker(object):
    """"""

    def __init__(
            self,
            redis_connection: Redis
    ) -> None:
        """
        :param redis_connection: async connector to redis
        """
        self._connection = redis_connection

    async def __aenter__(self):
        await self._connection.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        return self._connection.__aexit__(*args, **kwargs)

    @staticmethod
    def create_unique_identifier(*args):
        return hashlib.md5(
            "/".join(
                map(lambda x: str(x), args)
            ).encode()
        ).hexdigest()

    @staticmethod
    def create_mutex_key(identifier: str):
        return f"{identifier}_mutex"

    async def lock(
            self,
            key: str = None,
            duration: float = 10.0,
            force: bool = False
    ) -> Optional[Lock]:
        """"""
        lock = Lock(
            lock_key=key,
            lock_duration=duration,
            priority_mode=force
        )
        lock_result = await self._connection.set(
            name=lock.redis_key,
            value="|".join([lock.identifier, str(int(lock.priority_mode))]),
            px=int(lock.duration * 1000),
            nx=not force
        )
        if not lock_result:
            raise LockException("Cannot to set lock")
        # expire_result = await self._connection.expire(name=lock.redis_key, time=duration)
        # print(f"EXPIRE RESULT {key}: {expire_result}")
        return lock

    async def get_current_lock(self, lock_key: str = None) -> Optional[Lock]:
        """"""
        lock_data, ttl = await asyncio.gather(
            *[
                self._connection.get(lock_key),
                self._connection.pttl(lock_key)
            ]
        )

        if not lock_data:
            return None
        lock_data: str
        value, priority = lock_data.split("|")
        return Lock(
            lock_key=lock_key,
            lock_duration=float(ttl / 1000),
            priority_mode=bool(int(priority)),
            identifier=value,
        )

    async def extend_lock(self, lock: Lock, duration: int = None) -> Optional[Lock]:
        """"""
        if duration:
            lock.duration = duration
        redis_lock_value = await self._connection.get(lock.redis_key)
        if not redis_lock_value:
            raise LockException("Redis key is not exists")

        redis_lock_value, priority = redis_lock_value.split("|")
        if not redis_lock_value == lock.identifier:
            raise LockException("Resource is locked with another identifier")
        lock_result = await self._connection.pexpire(name=lock.redis_key, time=int(lock.duration * 1000))
        if not lock_result:
            raise LockException("Redis key is not exists")
        return lock

    async def release_lock(self, lock: Lock, force: bool = False) -> Optional[Lock]:
        """"""
        redis_lock_value = await self._connection.get(lock.redis_key)
        if not redis_lock_value:
            raise LockException("Redis key is not exists")

        redis_lock_value, priority = redis_lock_value.split("|")
        if not redis_lock_value:
            return lock
        if not redis_lock_value == lock.identifier and not force:
            raise ReleaseLockException("Resource is locked with another identifier")
        release_result = await self._connection.delete(lock.redis_key)
        if not release_result:
            raise ReleaseLockException("Redis key is not exists")
        return lock

    async def master_capture_lock(
            self,
            lock_key: str,
            max_expire_lock_time: int = 5,
            duration: int = None,
    ) -> Optional[Lock]:
        """"""
        lock_data, ttl = await asyncio.gather(
            *[
                self._connection.get(lock_key),
                self._connection.ttl(lock_key)
            ]
        )
        if not lock_data:
            result = await self.lock(
                key=lock_key,
                duration=duration,
                force=True
            )
            return result
        lock_data: str
        value, priority = lock_data.split("|")
        print(f"Current lock info:\tkey: `{lock_key}`\t|value: `{value}`\t|ttl: `{ttl / 1000}`\t|pr: `{priority}`")
        if ttl == -1:
            # print(f"NO EXPIRE for {lock_key}")
            raise LockException(
                f"Expire for key `{lock_key}` is not set."
            )
        elif ttl / 1000 <= max_expire_lock_time:
            result = await self.lock(
                key=lock_key,
                duration=duration,
                force=True
            )
            # print(f"RESULT: {result}")
            return result
        else:
            raise LockException(
                f"Can't get mutex. ttl: `{ttl / 1000}`\tmax_expire: `{max_expire_lock_time}`."
            )
