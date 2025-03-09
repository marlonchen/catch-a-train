import json
import time

from prometheus_client import CollectorRegistry, Counter, Histogram

from train_catcher.adaptor.direction_api import DirectionApi
from train_catcher.data.rail import RAIL_SYSTEMS
from train_catcher.data.station import Station
from train_catcher.service.geojson_builder import GeoJsonBuilder
from train_catcher.service.persistence import PersistenceService
from train_catcher.util import get_logger

# Metrics
METRICS_REG = CollectorRegistry()

REQUESTS = Counter('station_finder_requests_total', 'Total requests', registry=METRICS_REG)
LATENCY = Histogram('station_finder_latency_seconds', 'Request latency', registry=METRICS_REG)
CACHE_HITS = Counter('station_finder_cache_hits_total', 'Cache hits', registry=METRICS_REG)


class NotWithinServiceAreaException(Exception):
    ...


class StationFinder:
    _persistence_service: PersistenceService = PersistenceService()
    _logger = get_logger(__name__)
    
    def _find_it(self, lat: float, lon: float) -> tuple[Station, float]:
        for _, rail in RAIL_SYSTEMS.items():
            nearest_station, min_distance = rail.get_nearest_station(lat, lon)
            if nearest_station:
                break
        if not nearest_station:
            raise NotWithinServiceAreaException(
                f"Location ({lat}, {lon}) is outside service area"
            )
        return nearest_station, min_distance

    def find_nearest_station(self, lat: float, lon: float) -> dict:
        """Find nearest train station and return in GeoJSON format"""
        start_time = time.time()
        REQUESTS.inc()

        # Check cache
        cached_result = self._persistence_service.load_direction(lat, lon)
        if cached_result:
            CACHE_HITS.inc()
            self._logger.info(f"Cache hit for {lat=}, {lon=}.")
            return json.loads(cached_result)

        self._persistence_service.begin_find(lat, lon)
        
        try:
            station, distance = self._find_it(lat, lon)
            direction = DirectionApi.find_walking_direction(
                lat, lon, 
                station.latitude, station.longitude
            )

            builder = GeoJsonBuilder()
            builder.starting_point(lat, lon)
            builder.destination_station(station, distance)
            builder.direction(direction)
            result = builder.build()

            self._persistence_service.save_direction(lat, lon, json.dumps(result))
            
            LATENCY.observe(time.time() - start_time)
            return result
        except NotWithinServiceAreaException:
            raise
        except Exception:
            self._logger.exception(f"Error finding nearest station for {lat=}, {lon=}.")
            raise
        finally:
            self._persistence_service.end_find(lat, lon)
