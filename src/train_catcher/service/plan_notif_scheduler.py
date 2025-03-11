from datetime import datetime, timedelta

from train_catcher.adaptor.dynamo import DynamoTable
from train_catcher.adaptor.sms import SmsSender
from train_catcher.util import EASTERN_TZ, get_logger

RECORD_TABLE = 'notif_record_table'
NOTIFICATION_SCHEDULE_TABLE = 'notif_schedule_table'


class PlanNotificationScheduler:
    _logger = get_logger(__name__)
    _sms = SmsSender()

    def __init__(self, phone: str):
        self._phone = phone

    def _validate(self, plan: dict) -> bool:
        table = DynamoTable(RECORD_TABLE)
        records = table.query_by_hash_key_and_sort_key_datetime_range(
            'hash_key', self._phone,
            'sort_key', datetime.now(EASTERN_TZ) - timedelta(minutes=5)
        )
        return len(records) < 1

    def _format_message(self, plan: dict) -> str:
        station = plan['station']
        train = plan['next_train']
        train_time = datetime.fromisoformat(train['sched_time']).strftime('%I:%M %p')
        return (
            f"SEPTA line {train['line']} "
            f"{'Northbound' if train['direction'] == 'N' else 'Southbound'} "
            f"to arrive {station} at {train_time}"
        )
    
    def notify(self, plan: dict):
        if not self._validate(plan):
            self._logger.info('too many messages to the customer, skip notificatoin')
            return
        self._sms.send(self._phone, self._format_message(plan))
        table = DynamoTable(RECORD_TABLE)
        table.write_item(
            {
                'hash_key': self._phone,
                'sort_key': datetime.now(EASTERN_TZ),
                'phone': self._phone,
                'plan': plan
            }
        )

    def schedule(self, plan: dict):
        if not self._phone:
            self._logger.info('no phone number, skip notificatoin')
            return
        if not plan:
            self._logger.info('plan is not created, skip notificatoin')
            return
        if plan['must_leave_now']:
            self.notify(plan)
            return
        # schedule notification
        table = DynamoTable(NOTIFICATION_SCHEDULE_TABLE)
        wait_time_to_notify = (
            datetime.fromisoformat(plan['time_to_leave'])
            - datetime.now()
        )
        table.write_item(
            {
                'hash_key': self._phone,
                'phone': self._phone,
                'plan': plan,
                'ttl': wait_time_to_notify.total_seconds()
            }
        )
