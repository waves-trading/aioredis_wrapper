""""""

from typing import Optional

from aioredis import create_redis


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
            request_timeout: int = 2,
            **__
    ) -> None:
        self._host = host
        self._port = port
        self._password = password
        self._redis = None
        self._timeout = request_timeout
        self._db = db

    @property
    def address(self):
        return self._host, self._port

    async def __aenter__(self):
        self._redis = await create_redis(
            (self._host, self._port),
            db=self._db,
            password=self._password,
            encoding="utf-8",
            timeout=self._timeout
        )
        return self._redis

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._redis.close()
