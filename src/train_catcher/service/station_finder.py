import json
import time

from geopy.distance import geodesic
from prometheus_client import Counter, Histogram

from train_catcher.adaptor.direction_api import DirectionApi
from train_catcher.adaptor.kmz_reader import KmzReader
from train_catcher.service.geojson_builder import GeoJsonBuilder
from train_catcher.service.persistence import PersistenceService

# Metrics
REQUESTS = Counter('station_finder_requests_total', 'Total requests')
LATENCY = Histogram('station_finder_latency_seconds', 'Request latency')
CACHE_HITS = Counter('station_finder_cache_hits_total', 'Cache hits')


class StationFinder:
    _persistence_service: PersistenceService = PersistenceService()
    
    def __init__(self, kmz_file: str):
        self._kmz_file = kmz_file

    def _find_it(self, lat: float, lon: float) -> dict:
        nearest_station = None
        min_distance = float('inf')
        
        stations = KmzReader.read(self._kmz_file)

        for station in stations:
            distance = geodesic(
                (lat, lon), 
                (station['Latitude'], station['Longitude'])
            ).miles
            
            if distance < min_distance:
                min_distance = distance
                nearest_station = station
        
        return {
            'Longitude': nearest_station['Longitude'],
            'Latitude': nearest_station['Latitude'],
            'Station': nearest_station['Station'],
            'Line': nearest_station['Line'],
            'Distance': min_distance
        }

    def find_nearest_station(self, lat: float, lon: float) -> dict:
        """Find nearest train station and return in GeoJSON format"""
        start_time = time.time()
        REQUESTS.inc()

        # Check cache
        cached_result = self._persistence_service.load_direction(lat, lon)
        if cached_result:
            CACHE_HITS.inc()
            return json.loads(cached_result)

        self._persistence_service.begin_find(lat, lon)
        
        try:
            station = self._find_it(lat, lon)
            direction = DirectionApi.find_walking_direction(
                lat, lon, 
                station['Latitude'], station['Longitude']
            )

            builder = GeoJsonBuilder()
            builder.starting_point(lat, lon)
            builder.destination_station(station)
            builder.direction(direction)
            result = builder.build()

            self._persistence_service.save_direction(lat, lon, json.dumps(result))
            
            LATENCY.observe(time.time() - start_time)
            return result
        finally:
            self._persistence_service.end_find(lat, lon)
