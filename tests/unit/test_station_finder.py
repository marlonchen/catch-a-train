from unittest.mock import patch
import pytest

from stub.dict_cache import DictCache
from train_catcher.adaptor.sms import SmsSender
from train_catcher.data.rail import RAIL_SYSTEM
from train_catcher.service.notifier import Notifier
from train_catcher.service.station_finder import StationFinder


@patch('train_catcher.service.persistence.the_cache')
@patch.object(SmsSender,'send')
def test_when_a_location_then_it_should_find_direction_to_a_station(
    sms_send,
    mock_cache
):
    # Arrange
    station_finder = StationFinder(RAIL_SYSTEM.get_data_file())
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


@pytest.mark.parametrize('lat, lon, within_range', [
    (39.9726, -75.1602, True),
    (40.9726, -75.1602, False),
    (39.9726, -76.1602, False),
    (38.9726, -75.1602, False)
])
def test_given_a_location_then_it_should_return_if_it_is_outside_service_area(
    lat: float, lon: float, within_range: bool
):
    # Arrange
    
    # Act
    with_in_range = RAIL_SYSTEM.is_within_service_area(lat, lon)
    
    # Assert
    assert with_in_range == within_range
