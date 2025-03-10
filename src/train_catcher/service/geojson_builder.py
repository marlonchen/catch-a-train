from __future__ import annotations

from train_catcher.data.station import Station


class GeoJsonBuilder:
    def __init__(self):
        self._features = []

    def starting_point(self, lat: float, lon: float) -> GeoJsonBuilder:
        self._features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [lon, lat]
            },
            'properties': {
                'location_type': 'Starting Location'
            }
        })
        return self
    
    def destination_station(self, station: Station, distance: float) -> GeoJsonBuilder:
        self._features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(station.longitude), float(station.latitude)]
            },
            "properties": {
                'location_type': 'Destination Station',
                "name": station.name,
                "line": station.line,
                "distance": distance
            }
        })
        return self
    
    def routes(self, routes: dict) -> GeoJsonBuilder:
        route = routes['routes'][0]
        steps = route.get('legs', [{}])[0].get('steps', [])
        waypoints = routes.get('waypoints', [])

        self._features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    [waypoint['location'][1], waypoint['location'][0]]
                    for waypoint in waypoints
                    if 'location' in waypoint
               ]
            },
            'properties': {
                'direction_type': 'Walking Direction',
                'distance': route['distance'],
                'duration': route['duration'],
                'steps': [
                    step['maneuver']['instruction']
                    for step in steps
                    if 'instruction' in step.get('maneuver', {})
                ]
            }
        })
        return self

    def build(self) -> dict:
        return {
            'type': 'FeatureCollection',
            'features': self._features
        }
