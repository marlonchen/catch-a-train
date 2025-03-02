from functools import cache
import requests


class DirectionApi:
    @cache
    @staticmethod
    def find_walking_direction(start_lat: float, start_lon: float, 
                               end_lat: float, end_lon: float) -> str:
        """Get walking directions using OpenStreetMap"""
        url = f"https://router.project-osrm.org/route/v1/foot/{start_lon},{start_lat};{end_lon},{end_lat}"
        response = requests.get(url)
        return response.json()
