""""""

from typing import Optional

# from aioredis import create_redis, create_redis_pool
from aioredis import Redis


class RedisConnection(object):
    """
    Class for async redis connection context manager.
    """

    def __init__(
            self,
            *_,
            host: str = "127.0.0.1",
            port: int = 6379,
            password: Optional[str] = None,
            db: int = 0,
            timeout: int = 2,
            **__
    ) -> None:
        self._host = host
        self._port = port
        self._password = password
        self._timeout = timeout
        self._db = db
        self._redis = Redis(
            host=self._host,
            port=self._port,
            db=self._db,
            password=self._password,
            socket_connect_timeout=self._timeout,
            socket_timeout=self._timeout,
            decode_responses=True,
            encoding="utf-8"
        )

    @property
    def address(self):
        return self._host, self._port, self._db

    async def __aenter__(self):
        return await self._redis.initialize()
        # self._redis = await create_redis_pool(
        #     (self._host, self._port),
        #     db=self._db,
        #     password=self._password,
        #     encoding="utf-8",
        #     timeout=self._timeout
        # )
        # return self._redis

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._redis.close()
        # return await self._redis.wait_closed()
