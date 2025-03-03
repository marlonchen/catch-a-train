from __future__ import annotations

from abc import abstractmethod

import redis


def the_cache() -> CacheStore:
    return RedisCache()


class CacheStore:
    @abstractmethod
    def get(self, cache_key: str) -> str:
        ...

    @abstractmethod
    def set(self, cache_key: str, value: str, ttl: int) -> None:
        ...

    @abstractmethod
    def delete(self, cache_key: str) -> None:
        ...


class RedisCache(CacheStore):
    _redis_client: redis.Redis = None

    def _get_redis_client(self) -> redis.Redis:
        if self._redis_client is None:
            self._redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0
            )
        return self._redis_client

    def get(self, cache_key: str) -> str:
        return self._get_redis_client().get(cache_key)

    def set(self, cache_key: str, value: str, ttl: int) -> None:
        self._get_redis_client().setex(cache_key, ttl, value)

    def delete(self, cache_key: str) -> None:
        self._get_redis_client().delete(cache_key)


class DictCache(CacheStore):
    _dict: dict = {}

    def get(self, cache_key: str) -> str:
        return self._dict.get(cache_key)

    def set(self, cache_key: str, value: str, ttl: int) -> None:
        self._dict[cache_key] = value

    def delete(self, cache_key: str) -> None:
        del self._dict[cache_key]
