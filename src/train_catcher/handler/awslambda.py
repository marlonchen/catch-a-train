from fastapi import HTTPException

from train_catcher.data.rail import RAIL_SYSTEM
from train_catcher.service.notifier import Notifier
from train_catcher.service.persistence import TimeoutException
from train_catcher.service.station_finder import StationFinder


def handler(event, context):
    # extract data from event
    query_string = event['queryStringParameters']
    lat = query_string['lat']
    lon = query_string['lon']
    phone = query_string.get('phone')

    if not RAIL_SYSTEM.is_within_service_area(lat, lon):
        raise HTTPException(
            status_code=400,
            detail="Location is outside service area"
        )

    try:
        finder = StationFinder(RAIL_SYSTEM.get_data_file())
        direction = finder.find_nearest_station(lat, lon)
        notifier = Notifier(phone)
        direction = notifier.send_walking_direction(direction)
        return direction
    except TimeoutException:
        raise HTTPException(status_code=429, detail="Location search in progress")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
