"""
Device configuration Lambda handlers
"""
import json
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
config_table = dynamodb.Table(os.environ['SST_Table_tableName_config'])

def get(event, context):
    """Get device configuration"""
    # Extract device ID from path or use default
    device_id = event.get('pathParameters', {}).get('deviceId', 'default')

    try:
        response = config_table.get_item(
            Key={'deviceId': device_id, 'timestamp': 0}
        )

        config = response.get('Item', get_default_config())

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(config, default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def update(event, context):
    """Update device configuration"""
    device_id = event.get('pathParameters', {}).get('deviceId', 'default')

    try:
        config = json.loads(event['body'])
        config['deviceId'] = device_id
        config['timestamp'] = 0  # Current config always at timestamp 0
        config['lastUpdated'] = datetime.now().isoformat()

        config_table.put_item(Item=config)

        return {
            'statusCode': 200,
            'body': json.dumps({'success': True, 'message': 'Config updated'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def get_default_config():
    """Return default configuration"""
    return {
        'deviceId': 'default',
        'wifi': {
            'ssid': 'your-network',
            'password': 'your-password'
        },
        'location': {
            'bounds_box': '51.6,51.4,-0.3,-0.1',
            'name': 'Central London'
        },
        'active_layout': 'classic',
        'query_delay': 30,
        'display': {
            'plane_color': '0x4B0082',
            'plane_speed': 0.04,
            'text_speed': 0.04,
            'pause_between_scrolling': 3
        }
    }
