import os

from geopy.distance import geodesic


class RailSystemInfo:
    """
    This can be refactored to pick one based on user's location,
    but for now, we will use the Philadelphia regional rail system.
    """
    def __init__(self, *, data_file: str, lat: float, lon: float, max_radius: float):
        self._data_file = data_file
        self._lat = lat
        self._lon = lon
        self._max_radius = max_radius

    def get_data_file(self):
        return self._data_file
    
    def is_within_service_area(self, lat, lon):
        """
        Checks if the provided latitude and longitude are within the defined service area.
        """
        distance = geodesic((self._lat, self._lon), (lat, lon)).miles
        return distance <= self._max_radius


RAIL_SYSTEM = RailSystemInfo(
    data_file=os.path.join(
        os.path.dirname(__file__),
        'SEPTARegionalRailStations2016.kmz'
    ),
    lat=39.9526,
    lon=-75.165,
    max_radius=50  # since longest line is 41 miles based wikipedia
)
