from fastapi import HTTPException

from train_catcher.data.path import STATION_FILE_PATH
from train_catcher.service.notifier import Notifier
from train_catcher.service.persistence import TimeoutException
from train_catcher.service.station_finder import StationFinder


def handler(event, context):
    # extract data from event
    query_string = event['queryStringParameters']
    lat = query_string['lat']
    lon = query_string['lon']
    phone = query_string.get('phone')

    try:
        finder = StationFinder(STATION_FILE_PATH)
        direction = finder.find_nearest_station(lat, lon)
        notifier = Notifier(phone)
        direction = notifier.send_walking_direction(direction)
        return direction
    except TimeoutException:
        raise HTTPException(status_code=429, detail="Location search in progress")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
