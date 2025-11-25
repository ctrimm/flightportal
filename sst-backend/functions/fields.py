"""
Available fields Lambda handler
"""
import json

AVAILABLE_FIELDS = {
    "fields": [
        {
            "id": "flight_number",
            "name": "Flight Number",
            "description": "Flight number (e.g., BA123)",
            "path": "identification.number.default",
            "type": "string",
            "category": "identification"
        },
        {
            "id": "airline_name",
            "name": "Airline Name",
            "description": "Full airline name",
            "path": "airline.name",
            "type": "string",
            "category": "airline"
        },
        {
            "id": "aircraft_code",
            "name": "Aircraft Code",
            "description": "Aircraft type code (e.g., A320)",
            "path": "aircraft.model.code",
            "type": "string",
            "category": "aircraft"
        },
        {
            "id": "route_codes",
            "name": "Route Codes",
            "description": "Origin-Destination codes",
            "type": "computed",
            "category": "route"
        },
        {
            "id": "altitude",
            "name": "Altitude",
            "description": "Current altitude in feet",
            "path": "trail.0.alt",
            "type": "number",
            "category": "position"
        },
        {
            "id": "speed",
            "name": "Speed",
            "description": "Current speed in knots",
            "path": "trail.0.spd",
            "type": "number",
            "category": "position"
        }
    ]
}

def list(event, context):
    """List all available fields"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(AVAILABLE_FIELDS)
    }
