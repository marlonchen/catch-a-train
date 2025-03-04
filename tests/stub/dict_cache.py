from train_catcher.adaptor.cache_store import CacheStore


class DictCache(CacheStore):
    _dict: dict = {}

    def get(self, cache_key: str) -> str:
        return self._dict.get(cache_key)

    def set(self, cache_key: str, value: str, ttl: int) -> None:
        self._dict[cache_key] = value

    def delete(self, cache_key: str) -> None:
        del self._dict[cache_key]
