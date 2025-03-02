import os
from twilio.rest import Client


twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)
TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER')


class NotificationService:
    @classmethod
    def _send_sms(cls, to_number: str, message: str) -> None:
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
        
    @classmethod
    def _format_directions(cls, directions: dict) -> str:
        """
        Format OSRM walking directions into a concise SMS message.
        Returns a string with step-by-step directions.
        """
        if not directions or 'routes' not in directions or not directions['routes']:
            return "Sorry, directions are not available at this time."
        
        route = directions['routes'][0]
        steps = []
        
        # Get total distance and duration
        distance = round(route['distance'] / 1609.34, 1)  # Convert meters to miles
        duration = round(route['duration'] / 60)  # Convert seconds to minutes
        
        steps.append(f"Walk {distance} miles ({duration} mins):")
        
        # Format each step of the journey
        if 'legs' in route and route['legs']:
            for step in route['legs'][0].get('steps', []):
                instruction = step.get('maneuver', {}).get('instruction', '')
                if instruction:
                    steps.append(f"- {instruction}")
        
        # Combine all steps into a single message
        return "\n".join(steps)
    
    @classmethod
    def send_walking_directions(cls, phone: str, directions: dict) -> None:
        """Send notification to user"""
        if phone:
            # Send SMS with walking directions
            cls._send_sms(phone, cls._format_directions(directions))
