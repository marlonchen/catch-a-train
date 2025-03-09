from __future__ import annotations

import html

from dataclasses import dataclass
from fastkml import KML
from pygeoif.geometry import Point


@dataclass
class Station:
    name: str
    latitude: float
    longitude: float
    line: str

    @classmethod
    def _extract_name_from_kml_description(cls, description: str) -> str:
        rows = description.split('<tr')
        for row in rows:
            if 'Station_Na' in row:
                html_encoded = row.split('<td>')[2].split('</td>')[0]
                # return decoded html
                return html.unescape(html_encoded)
    
    @classmethod
    def from_kml(cls, data: KML) -> list[Station]:
        if not data.features or not data.features[0].features:
            return []
        return [
            Station(
                name=cls._extract_name_from_kml_description(feature.description),
                latitude=feature.geometry.y,
                longitude=feature.geometry.x,
                line=feature.name
            )
            for feature in data.features[0].features[0].features
            if hasattr(feature, 'geometry') and isinstance(feature.geometry, Point)
        ]

    
    @staticmethod
    def from_geojson(data: dict) -> list[Station]:
        return [
            Station(
                name=feature['properties']['NAME'],
                latitude=feature['geometry']['coordinates'][1],
                longitude=feature['geometry']['coordinates'][0],
                line=feature['properties']['LINE']
            )
            for feature in data['features']
        ]

