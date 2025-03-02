import os
from unittest.mock import patch
from train_catcher.adaptor.dist_cache import DictCache
from train_catcher.service.notification import NotificationService
from train_catcher.service.station_finder import StationFinder


@patch('train_catcher.service.persistence.the_cache')
@patch.object(NotificationService,'send_walking_directions')
def test_when_station_finder_is_created_then_it_should_have_a_name(
    mock_notification_send,
    mock_cache
):
    # Arrange
    current_directory = os.path.dirname(__file__)
    station_file_path = os.path.join(current_directory, '../../src/train_catcher/data/SEPTARegionalRailStations2016.kmz')
    station_finder = StationFinder(station_file_path)
    
    mock_cache.return_value = DictCache()

    # Act
    lat = 39.9526
    lon = -75.1652
    direction = station_finder.find_nearest_station(lat, lon)
    
    # Assert
    assert direction
