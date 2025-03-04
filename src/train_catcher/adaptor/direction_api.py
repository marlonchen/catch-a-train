from functools import cache
import os

import requests


class DirectionApi:
    @cache
    @staticmethod
    def find_walking_direction(start_lat: float, start_lon: float, 
                               end_lat: float, end_lon: float) -> str:
        """Get walking directions using OpenStreetMap"""
        root = os.getenv('DIRECTION_API_ROOT')
        url = f"{root}{start_lon},{start_lat};{end_lon},{end_lat}"
        response = requests.get(url)
        return response.json()
