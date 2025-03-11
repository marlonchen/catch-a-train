from functools import cache
import os

import requests


class DirectionApi:
    @cache
    @staticmethod
    def find_walking_direction(start_lat: float, start_lon: float, 
                               end_lat: float, end_lon: float) -> dict:
        """Get walking directions using OpenStreetMap"""
        root = os.getenv('DIRECTION_API_BASE_URL')
        url = f"{root}{start_lon},{start_lat};{end_lon},{end_lat}"
        response = requests.get(url)
        return response.json()
