import os

import requests

LINE_STATIONS = None


class TrainScheduleApi:
    """
    SEPTA for now
    """
    @classmethod
    def _get_url(cls) -> str:
        return os.getenv('SEPTA_TRAIN_SCHEDULE_URL', '')

    @classmethod
    def get_next_train(cls, station_name: str, direction: str, count: int) -> dict:
        """
        Retrieves the next train departure time from the SEPTA API.
        """
        url = f'{cls._get_url()}Arrivals/index.php'
        response = requests.get(
            url,
            params={
                "station": station_name,
                "direction": direction,
                "results": count
            }
        )
        response.raise_for_status()
        return response.json()
