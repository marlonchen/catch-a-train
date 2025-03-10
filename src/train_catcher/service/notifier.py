from train_catcher.adaptor.sms import SmsSender


class Notifier:
    _sms: SmsSender = None
    
    def __init__(self, phone: str = ''):
        # sms only at the moment
        self._phone = phone
        
    @staticmethod
    def _format_direction(routes: dict) -> str:
        """
        Format OSRM walking directions into a concise SMS message.
        Returns a string with step-by-step directions.
        """
        if not routes or routes.get('properties', {}).get('steps'):
            return "Sorry, directions are not available at this time."
        
        route = routes['properties']
        steps = []
        
        # Get total distance and duration
        distance = round(route['distance'] / 1609.34, 1)  # Convert meters to miles
        duration = round(route['duration'] / 60)  # Convert seconds to minutes
        
        steps.append(f"Walk {distance} miles ({duration} mins):")
        
        # Format each step of the journey
        for step in route['steps']:
            instruction = step.get('maneuver', {}).get('instruction', '')
            if instruction:
                steps.append(f"- {instruction}")
        
        # Combine all steps into a single message
        return "\n".join(steps)
    
    def send_walking_direction(self, direction: dict) -> str:
        """Send notification to user"""
        if not self._phone:
            return ''
        # Send SMS with walking directions
        routes = [
            feature
            for feature in direction['features']
            if feature['geometry']['type'] == 'LineString'
        ][0]
        instruction = self._format_direction(routes)
        SmsSender.send(self._phone, instruction)
        return instruction
