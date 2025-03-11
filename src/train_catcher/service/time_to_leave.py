from datetime import datetime, timedelta
from typing import Optional

from train_catcher.adaptor.direction_api import DirectionApi
from train_catcher.adaptor.train_schedule_api import TrainScheduleApi
from train_catcher.data.rail import RAIL_SYSTEMS
from train_catcher.data.station import Station
from train_catcher.util import EASTERN_TZ, get_logger

SAFETY_BUFFER_MINUTES = 5

SEPTA_GIS_LINE_NAMES = {
    # mapping from API line name to GIS line name
    "Airport": "Airport Line",
    "Chestnut Hill East": "Chestnut Hill East Line",
    "Chestnut Hill West": "Chestnut Hill West Line",
    "Cynwyd": "Cynwyd Line",
    "Fox Chase": "Fox Chase Line",
    "Lansdale/Doylestown": "Lansdale/Doylestown Line",
    "Media/Wawa": "Media/Wawa Line",
    "Manayunk/Norristown": "Manayunk/Norristown Line",
    "Paoli/Thorndale": "Paoli/Thorndale Line",
    "Trenton": "Trenton Line",
    "Warminster": "Warminster Line",
    "West Trenton": "West Trenton Line",
    "Wilmington/Newark": "Wilmington/Newark Line",
}

class TimeToLeavePlanner:
    _train_schedule_api: TrainScheduleApi = TrainScheduleApi()
    _logger = get_logger(__name__)

    @classmethod
    def _get_nearest_station_by_line(cls, lat: float, lon: float, line: str) -> Station:
        rail = RAIL_SYSTEMS['SEPTA Regional Rail']
        gis_line = SEPTA_GIS_LINE_NAMES[line]
        station, _ = rail.get_nearest_station_by_line(lat, lon, gis_line)
        return station

    @classmethod
    def _get_next_train(
            cls,
            station_name,
            line,
            direction,
            minutes_to_travel: int
    ) -> Optional[dict]:
        if direction.upper().startswith('N'):
            direction_param = 'N'
            direction_node = 'Northbound'
        else:
            direction_param = 'S'
            direction_node = 'Southbound'
        next_train = cls._train_schedule_api.get_next_train(station_name, direction_param, 50)
        data = [v for _, v in next_train.items()][0]
        if data and isinstance(data, list) and data[0] and direction_node in data[0]:
            time_to_arrive = datetime.now(EASTERN_TZ) + timedelta(minutes=minutes_to_travel)
            for train in data[0][direction_node]:
                # find the line that passes the station
                if train["line"].lower() == line.lower():
                    departure_time_str = train["depart_time"]
                    departure_time = EASTERN_TZ.localize(datetime.fromisoformat(departure_time_str))
                    # find the train with enough time to walk there
                    if departure_time >= time_to_arrive:
                        return train
            return None
        else:
            cls._logger.warning("no data returned from api")
            return None
    
    @classmethod
    def _get_walking_time_in_minutes(
        cls,
        lat: float, lon: float,
        station: Station
    ) -> int:
        routes = DirectionApi.find_walking_direction(
            lat, lon,
            station.latitude, station.longitude
        )
        route = routes.get('routes', [0])[0]
        return route['duration'] / 60

    @classmethod
    def plan_time_to_leave(
            cls,
            lat: float,
            lon: float,
            line: str,
            direction: str
    ) -> dict:
        try:
            # step 1: find nearest station by line
            station = cls._get_nearest_station_by_line(lat, lon, line)

            # step 2: find the next train of the line
            travel_time_minutes = cls._get_walking_time_in_minutes(lat, lon, station)
            next_train = cls._get_next_train(station.name, line, direction, travel_time_minutes)
            if not next_train:
                cls._logger.info(
                    "no matching train found for '%s' of line '%s' and direction '%s'",
                    station.name, line, direction
                )
                return {}
            
            # step 3: find when to leave
            departure_time_str = next_train["depart_time"]
            departure_time = EASTERN_TZ.localize(datetime.fromisoformat(departure_time_str))
            now = datetime.now(EASTERN_TZ)
            must_leave_at = departure_time - timedelta(minutes=travel_time_minutes + SAFETY_BUFFER_MINUTES)

            return {
                "next_train": next_train,
                "must_leave_now": must_leave_at <= now,
                "time_to_leave": max(must_leave_at, now)
            }

        except (ValueError, KeyError):
            cls._logger.exception("Error parsing SEPTA data")
            raise
