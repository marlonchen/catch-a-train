import os

import requests


class TrainScheduleApi:
    """
    SEPTA for now
    """
    @classmethod
    def _get_url(cls) -> str:
        return os.getenv('SEPTA_TRAIN_SCHEDULE_URL')

    @classmethod
    def get_next_train(cls, station_name: str, direction: str, count: int) -> list[dict]:
        """
        Retrieves the next train departure time from the SEPTA API.
        """
        response = requests.get(
            cls._get_url(),
            params={
                "station": station_name,
                "direction": direction,
                "results": count
            }
        )
        response.raise_for_status()
        return response.json()
