from functools import cache
from zipfile import ZipFile
from fastkml import kml
from pygeoif.geometry import Point

class KmzReader:
    @cache
    @staticmethod
    def read(kmz_path: str) -> list:
        """Load and parse KMZ file containing station data"""
        stations = []
        
        # Open KMZ file (which is a ZIP containing KML)
        with ZipFile(kmz_path) as kmz:
            # KMZ should contain a doc.kml file
            kml_content = kmz.read('doc.kml')
            
            # Parse KML content
            k = kml.KML.from_string(kml_content.decode('utf-8'))
            if not k.features or not k.features[0].features:
                return stations
            
            # Extract station data from KML
            document = k.features[0].features
            for feature in document[0].features:
                # Each placemark represents a station
                if hasattr(feature, 'geometry') and isinstance(feature.geometry, Point):
                    station = {
                        'Station': feature.name,
                        'Line': feature.description if feature.description else 'Unknown',
                        'Longitude': feature.geometry.x,
                        'Latitude': feature.geometry.y
                    }
                    stations.append(station)
        
        return stations
