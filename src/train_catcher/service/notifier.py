from train_catcher.adaptor.sms import SmsSender


class Notifier:
    _sms: SmsSender = None
    
    def __init__(self, phone: str = ''):
        # sms only at the moment
        self._phone = phone
        
    @staticmethod
    def _format_direction(direction: dict) -> str:
        """
        Format OSRM walking directions into a concise SMS message.
        Returns a string with step-by-step directions.
        """
        if not direction or 'routes' not in direction or not direction['routes']:
            return "Sorry, directions are not available at this time."
        
        route = direction['routes'][0]
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
    
    def send_walking_direction(self, directions: dict) -> None:
        """Send notification to user"""
        if self._phone:
            # Send SMS with walking directions
            SmsSender.send(self._phone, self._format_direction(directions))
