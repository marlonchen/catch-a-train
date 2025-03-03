import os

from twilio.rest import Client

from train_catcher.util import get_logger

TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER')


class SmsSender:
    _twilio_client: Client = None
    _logger = get_logger(__name__)
    
    @classmethod
    def _get_client(cls) -> Client:
        if cls._twilio_client is None:
            cls._twilio_client = Client(
                os.getenv('TWILIO_ACCOUNT_SID'),
                os.getenv('TWILIO_AUTH_TOKEN'),
                region='local'
            )
        return cls._twilio_client

    @classmethod
    def send(cls, to_number: str, message: str) -> None:
        """
        Send SMS using Twilio.
        Handles formatting of phone numbers and any Twilio errors.
        """
        if not TWILIO_FROM_NUMBER:
            return
        
        try:
            # Format phone number (remove any spaces, dashes, etc)
            formatted_number = ''.join(filter(str.isdigit, to_number))
            if not formatted_number.startswith('1'):
                formatted_number = '1' + formatted_number
            formatted_number = '+' + formatted_number

            # Send message via Twilio
            cls._get_client().messages.create(
                body=message,
                from_=TWILIO_FROM_NUMBER,
                to=formatted_number
            )
        except Exception:
            # Log error but don't fail the main request
            cls._logger.exception('Failed to send SMS.')
