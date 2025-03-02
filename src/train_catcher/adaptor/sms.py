import os
from twilio.rest import Client

# Initialize Twilio client
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)
TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER')

def send_sms(to_number: str, message: str) -> None:
    """
    Send SMS using Twilio.
    Handles formatting of phone numbers and any Twilio errors.
    """
    try:
        # Format phone number (remove any spaces, dashes, etc)
        formatted_number = ''.join(filter(str.isdigit, to_number))
        if not formatted_number.startswith('1'):
            formatted_number = '1' + formatted_number
        formatted_number = '+' + formatted_number

        # Send message via Twilio
        twilio_client.messages.create(
            body=message,
            from_=TWILIO_FROM_NUMBER,
            to=formatted_number
        )
    except Exception as e:
        # Log error but don't fail the main request
        print(f"SMS sending failed: {str(e)}")
