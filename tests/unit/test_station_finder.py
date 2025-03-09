from unittest.mock import patch
import pytest

from stub.dict_cache import DictCache
from train_catcher.adaptor.sms import SmsSender
from train_catcher.data.rail import RAIL_SYSTEMS
from train_catcher.service.notifier import Notifier
from train_catcher.service.station_finder import StationFinder


@patch('train_catcher.service.persistence.the_cache')
@patch.object(SmsSender,'send')
def test_given_a_philadelphia_location_then_it_should_find_direction_to_a_station(
    sms_send,
    mock_cache
):
    # Arrange
    station_finder = StationFinder()
    phone = '555-555-5555'
    
    mock_cache.return_value = DictCache()

    # Act
    lat = 39.9526
    lon = -75.1652
    direction = station_finder.find_nearest_station(lat, lon)
    instruction = Notifier(phone).send_walking_direction(direction)
    
    # Assert
    assert len(direction['features']) == 3
    for feature in direction['features']:
        if feature['properties'].get('location_type') == 'Starting Location':
            assert feature['geometry']['coordinates'] == [lon, lat]
        elif feature['properties'].get('location_type') == 'Destination Station':
            assert feature['properties']['name'] == 'Suburban Station'
        elif feature['properties'].get('direction_type') == 'Walking Direction':
            assert feature['geometry']['type'] == 'LineString'
            assert len(feature['geometry']['coordinates']) > 0
            assert feature['properties']['distance'] > 0

    sms_send.assert_called_once()
    # assert instruction


@patch('train_catcher.service.persistence.the_cache')
def test_given_a_dc_location_then_it_should_find_direction_to_a_station(
    mock_cache
):
    # Arrange
    station_finder = StationFinder()
    
    mock_cache.return_value = DictCache()

    # Act
    lat = 38.8951
    lon = -77.0364
    direction = station_finder.find_nearest_station(lat, lon)
    
    # Assert
    assert len(direction['features']) == 3
    for feature in direction['features']:
        if feature['properties'].get('location_type') == 'Starting Location':
            assert feature['geometry']['coordinates'] == [lon, lat]
        elif feature['properties'].get('location_type') == 'Destination Station':
            assert feature['properties']['name'] == 'McPherson Sq'
        elif feature['properties'].get('direction_type') == 'Walking Direction':
            assert feature['geometry']['type'] == 'LineString'
            assert len(feature['geometry']['coordinates']) > 0
            assert feature['properties']['distance'] > 0


@pytest.mark.parametrize('lat, lon, within_range', [
    (39.9526, -75.1652, True),
    (40.9526, -75.1652, False),
    (39.9526, -76.1652, False),
    (38.9526, -75.1652, False)
])
def test_given_a_location_then_it_should_return_if_it_is_outside_service_area(
    lat: float, lon: float, within_range: bool
):
    # Arrange
    rail_system = RAIL_SYSTEMS['SEPTA Regional Rail']
    
    # Act
    station, distance = rail_system.get_nearest_station(lat, lon)
    
    # Assert
    assert (station is not None) == within_range
