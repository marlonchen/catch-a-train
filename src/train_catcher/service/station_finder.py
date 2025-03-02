import json
import time

from geopy.distance import geodesic
from prometheus_client import Counter, Histogram

from train_catcher.adaptor.kmz_reader import KmzReader
from train_catcher.service.notification import NotificationService
from train_catcher.service.persistence import PersistenceService

# Metrics
REQUESTS = Counter('station_finder_requests_total', 'Total requests')
LATENCY = Histogram('station_finder_latency_seconds', 'Request latency')
CACHE_HITS = Counter('station_finder_cache_hits_total', 'Cache hits')


class StationFinder:
    _persistence_service: PersistenceService = PersistenceService()
    _notification_service: NotificationService = NotificationService()
    
    def __init__(self, kmz_file: str):
        self._kmz_file = kmz_file

    @staticmethod
    def _to_geojson(station: dict, distance: float) -> dict:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(station['Longitude']), float(station['Latitude'])]
            },
            "properties": {
                "name": station['Station'],
                "line": station['Line'],
                "distance": distance
            }
        }        

    def _find_nearest_station(self, lat: float, lon: float) -> dict:
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
        
        return self._to_geojson(nearest_station, min_distance)

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
            station = self._find_nearest_station(lat, lon)
            self._notification_service.send_walking_directions(
                lat, lon,
                station['geometry']['coordinates'][1],
                station['geometry']['coordinates'][0]
            )
            self._persistence_service.save_direction(lat, lon, json.dumps(station))
            
            LATENCY.observe(time.time() - start_time)
            return station
        finally:
            self._persistence_service.end_find(lat, lon)
