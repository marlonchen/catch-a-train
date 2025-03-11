from unittest.mock import patch

from freezegun import freeze_time

from train_catcher.adaptor.dynamo import DynamoTable
from train_catcher.adaptor.sms import SmsSender
from train_catcher.service.plan_notif_scheduler import PlanNotificationScheduler


@freeze_time('2024-01-01 10:00:00')
@patch.object(DynamoTable, 'write_item')
@patch.object(DynamoTable, 'query_by_hash_key_and_sort_key_datetime_range')
@patch.object(SmsSender, 'send')
def test_given_plan_within_5_minutes_then_send_notification(mock_sms_send, mock_dynamo_query, mock_dynamo_write):
    # Arrange
    phone = '+1234567890'
    plan = {
        'station': 'Station A',
        'next_train': {
            'line': 'Airport',
            'direction': 'N',
            'sched_time': '2024-01-01 10:05:00.000',
            'depart_time': '2024-01-01 10:06:00.000'
        },
        'must_leave_now': True,
        'time_to_leave': '2024-01-01 10:00:00'
    }
    mock_dynamo_query.return_value = []

    # Act
    scheduler = PlanNotificationScheduler(phone)
    scheduler.schedule(plan)

    # Assert
    mock_sms_send.assert_called_once()
    params = mock_sms_send.call_args_list[0].args
    assert params[0] == phone
    assert params[1] == 'SEPTA line Airport Northbound to arrive Station A at 10:05 AM'

    mock_dynamo_write.assert_called_once()
    params = mock_dynamo_write.call_args_list[0].args
    assert params[0]['phone'] == phone
    assert params[0]['plan'] == plan
    assert params[0]['hash_key'] == phone
    assert params[0]['sort_key'].isoformat() >= '2024-01-01 10:00:00.000'


@freeze_time('2024-01-01 10:00:00')
@patch.object(DynamoTable, 'write_item')
@patch.object(DynamoTable, 'query_by_hash_key_and_sort_key_datetime_range')
@patch.object(SmsSender, 'send')
def test_given_plan_more_than_5_minutes_then_write_to_dynamo_with_ttl(mock_sms_send, mock_dynamo_query, mock_dynamo_write):
    # Arrange
    phone = '+1234567890'
    plan = {
        'station': 'Station A',
        'next_train': {
            'line': 'Airport',
            'direction': 'N',
            'sched_time': '2024-01-01 10:15:00.000',
            'depart_time': '2024-01-01 10:16:00.000'
        },
        'must_leave_now': False,
        'time_to_leave': '2024-01-01 10:02:00'
    }
    mock_dynamo_query.return_value = []

    # Act
    scheduler = PlanNotificationScheduler(phone)
    scheduler.schedule(plan)

    # Assert
    mock_sms_send.assert_not_called()
    mock_dynamo_write.assert_called_once()
    params = mock_dynamo_write.call_args_list[0].args
    assert params[0]['phone'] == phone
    assert params[0]['plan'] == plan
    assert params[0]['hash_key'] == phone
    assert 60 < params[0]['ttl'] <= 120

