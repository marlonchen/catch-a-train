from train_catcher.service.time_to_leave import TimeToLeavePlanner

def test_happy_path():
    # Arrange
    # lat = 39.9089
    # lon = -75.4123
    # line = 'Media/Wawa'
    lat = 39.9656
    lon = -75.1810
    line = 'Airport Line'

    # Act
    plan = TimeToLeavePlanner().plan_time_to_leave(
        lat=lat,
        lon=lon,
        line=line,
        direction='S'
    )

    # Assert
    assert plan
