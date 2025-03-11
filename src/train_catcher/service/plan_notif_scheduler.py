from train_catcher.adaptor.dynamo import DynamoTable
from train_catcher.adaptor.sms import SmsSender
from train_catcher.util import get_logger

RECORD_TABLE = 'notif_record_table'
NOTIFICATION_SCHEDULE_TABLE = 'notif_schedule_table'


class PlanNotificationScheduler:
    _logger = get_logger(__name__)
    _sms = SmsSender()

    def __init__(self, phone: str):
        self._phone = phone

    def _validate(self, plan: dict) -> bool:
        table = DynamoTable(RECORD_TABLE)

    def _format_message(self, plan: dict) -> str:
        return (
            f"SEPTA line {plan['train']['line']} "
            f"{'Northbound' if plan['train']['direction'] == 'N' else 'Southbound'} "
            f"to arrive {plan['station']} "
            f"at {plan['train']['sched_time']}"
        )
    
    def notify(self, plan: dict):
        if not self._validate(plan):
            self._logger.info('too many messages to the customer, skip notificatoin')
            return
        self._sms.send(self._phone, self._format_message(plan))

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
        table = DynamoTable(RECORD_TABLE)
        table.write_item(
            {
                'hash_key': self._phone,
                'sort_key': plan['time_to_leave'],
                'phone': self._phone,
                'plan': plan
            }
        )
