from unittest.mock import patch

from stub.dict_cache import DictCache
from train_catcher.adaptor.sms import SmsSender
from train_catcher.data.path import STATION_FILE_PATH
from train_catcher.service.notifier import Notifier
from train_catcher.service.station_finder import StationFinder


@patch('train_catcher.service.persistence.the_cache')
@patch.object(SmsSender,'send')
def test_when_a_location_then_it_should_find_a_station(
    sms_send,
    mock_cache
):
    # Arrange
    station_finder = StationFinder(STATION_FILE_PATH)
    phone = '555-555-5555'
    
    mock_cache.return_value = DictCache()

    # Act
    lat = 39.9726
    lon = -75.1602
    direction = station_finder.find_nearest_station(lat, lon)
    instruction = Notifier(phone).send_walking_direction(direction)
    
    # Assert
    assert len(direction['features']) == 3
    for feature in direction['features']:
        if feature['properties'].get('location_type') == 'Starting Location':
            assert feature['geometry']['coordinates'] == [lon, lat]
        elif feature['properties'].get('location_type') == 'Destination Station':
            assert feature['properties']['name'] == 'Joint'
        elif feature['properties'].get('direction_type') == 'Walking Direction':
            assert feature['geometry']['type'] == 'LineString'
            assert len(feature['geometry']['coordinates']) > 0
            assert feature['properties']['distance'] > 0

    sms_send.assert_called_once()
    # assert instruction
