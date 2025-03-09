from fastapi import HTTPException

from train_catcher.service.notifier import Notifier
from train_catcher.service.persistence import TimeoutException
from train_catcher.service.station_finder import NotWithinServiceAreaException, StationFinder


def handler(event, context):
    # extract data from event
    query_string = event['queryStringParameters']
    lat = query_string['lat']
    lon = query_string['lon']
    phone = query_string.get('phone')

    try:
        finder = StationFinder()
        direction = finder.find_nearest_station(lat, lon)
        notifier = Notifier(phone)
        direction = notifier.send_walking_direction(direction)
        return direction
    except NotWithinServiceAreaException:
        raise HTTPException(status_code=400, detail="Location is outside service area")
    except TimeoutException:
        raise HTTPException(status_code=429, detail="Location search in progress")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
