from typing import Optional
from pydantic import BaseModel


class RedisSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    socket_timeout: int = 2
    unix_socket_path: Optional[str] = None
    decode_responses: bool = True
    username: Optional[str] = None
    encoding: str = "utf-8",
