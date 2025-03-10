from functools import cache
from zipfile import ZipFile

from fastkml import kml, KML
# from pygeoif.geometry import Point


class KmzReader:
    @cache
    @staticmethod
    def read(kmz_path: str) -> KML:
        """Load and parse KMZ file containing station data"""
        # Open KMZ file (which is a ZIP containing KML)
        with ZipFile(kmz_path) as kmz:
            # KMZ should contain a doc.kml file
            kml_content = kmz.read('doc.kml')
            
            # Parse KML content
            k = kml.KML.from_string(kml_content.decode('utf-8').encode())
            return k
