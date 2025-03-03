"""
Redis for now, permanent storage later, such as dynamoDB with TTL
"""
import time

from train_catcher.adaptor.cache_store import the_cache

DIRECTION_TTL = 60 * 60 * 24 * 7  # 1 week
PROCESSING_TIMEOUT = 6  # 6 seconds


class TimeoutException(Exception):
    ...


class PersistenceService:
    @staticmethod
    def load_direction(lat: float, lon: float) -> str:
        """Load walking directions from cache"""
        cache_key = f"station:{lat}:{lon}"
        direction = the_cache().get(cache_key)
        if direction:
            return direction
        
        # Implement concurrent request limiting
        start_time = time.time()
        while the_cache().get(f"processing:{cache_key}"):
            time.sleep(1)
            if time.time() - start_time > PROCESSING_TIMEOUT:
                raise TimeoutException("Location search in progress")

    @staticmethod
    def begin_find(lat: float, lon: float) -> None:
        """Begin finding walking directions"""
        cache_key = f"processing:{lat}:{lon}"
        the_cache().set(cache_key, "1", PROCESSING_TIMEOUT)

    @staticmethod
    def save_direction(lat: float, lon: float, directions: str) -> None:
        """Save walking directions in cache"""
        cache_key = f"station:{lat}:{lon}"
        the_cache().set(cache_key, directions, DIRECTION_TTL)

    @staticmethod
    def end_find(lat: float, lon: float) -> None:
        """End finding walking directions"""
        cache_key = f"processing:{lat}:{lon}"
        the_cache().delete(cache_key)
