import os

import json
from geopy.distance import geodesic

from train_catcher.adaptor.kmz_reader import KmzReader
from train_catcher.data.station import Station


class RailSystemInfo:
    """
    This can be refactored to pick one based on user's location,
    but for now, we will use the Philadelphia regional rail system.
    """
    def __init__(self, *, data_file: str, max_radius: float):
        self._data_file = data_file
        self._max_radius = max_radius
        self._stations: list[Station] = None

    def _get_stations(self) -> list[Station]:
        if not self._stations:
            # load stations once per instance
            file_path = os.path.join(
                os.path.dirname(__file__),
                self._data_file
            )
            if self._data_file.endswith('.kmz'):
                self._stations = Station.from_kml(KmzReader.read(file_path))
            elif self._data_file.endswith('.geojson'):
                with open(file_path, 'r') as file:
                    self._stations = Station.from_geojson(json.load(file))
            else:
                raise ValueError('Unsupported file format {self._data_file}')
        return self._stations

    def get_nearest_station(self, lat, lon) -> tuple[Station, float]:
        """
        Checks if the provided latitude and longitude are within the defined service area.
        """
        stations = self._get_stations()
        min_distance = self._max_radius
        nearest_station = None
        for station in stations:
            distance = geodesic(
                (lat, lon),
                (station.latitude, station.longitude)
            ).miles
            if distance < min_distance:
                min_distance = distance
                nearest_station = station
        return nearest_station, min_distance
        

RAIL_SYSTEMS = {
    'SEPTA Regional Rail': RailSystemInfo(
        data_file='SEPTARegionalRailStations2016.kmz',
        max_radius=10
    ),
    'DC Metro': RailSystemInfo(
        data_file='Metro_Stations_Regional.geojson',
        max_radius=15 # assuming DC is more walkable
    )
}
