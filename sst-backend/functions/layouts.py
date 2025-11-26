"""
Layout management Lambda handlers
"""
import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
layouts_table = dynamodb.Table(os.environ['SST_Table_tableName_layouts'])

# Default layouts
DEFAULT_LAYOUTS = {
    "layouts": [
        {
            "id": "classic",
            "name": "Classic",
            "description": "Original 3-row layout",
            "rows": [
                {"y": 4, "color": "0xEE82EE", "short_field": "flight_number", "long_field": "airline_name"},
                {"y": 15, "color": "0x4B0082", "short_field": "route_codes", "long_field": "route_full"},
                {"y": 25, "color": "0xFFA500", "short_field": "aircraft_code", "long_field": "aircraft_model"}
            ]
        },
        {
            "id": "detailed",
            "name": "Detailed",
            "description": "4-row layout with altitude and speed",
            "rows": [
                {"y": 2, "color": "0xEE82EE", "short_field": "flight_number", "long_field": "airline_name"},
                {"y": 11, "color": "0x4B0082", "short_field": "route_codes", "long_field": "route_with_altitude"},
                {"y": 20, "color": "0xFFA500", "short_field": "aircraft_code", "long_field": "aircraft_with_speed"},
                {"y": 29, "color": "0x00CED1", "short_field": "altitude", "long_field": "speed_and_heading"}
            ]
        }
    ]
}

def list(event, context):
    """List all layouts"""
    try:
        response = layouts_table.scan()
        layouts = response.get('Items', [])

        if not layouts:
            # Return defaults if no custom layouts
            return {
                'statusCode': 200,
                'body': json.dumps(DEFAULT_LAYOUTS)
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'layouts': layouts}, default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get(event, context):
    """Get specific layout"""
    layout_id = event['pathParameters']['id']

    try:
        response = layouts_table.get_item(
            Key={'layoutId': layout_id, 'version': 1}
        )

        layout = response.get('Item')
        if not layout:
            # Check defaults
            default_layout = next((l for l in DEFAULT_LAYOUTS['layouts'] if l['id'] == layout_id), None)
            if default_layout:
                return {
                    'statusCode': 200,
                    'body': json.dumps(default_layout)
                }
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Layout not found'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps(layout, default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def create(event, context):
    """Create new layout"""
    try:
        layout = json.loads(event['body'])
        layout['layoutId'] = layout['id']
        layout['version'] = 1

        layouts_table.put_item(Item=layout)

        return {
            'statusCode': 200,
            'body': json.dumps({'success': True, 'layout': layout}, default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def update(event, context):
    """Update layout"""
    layout_id = event['pathParameters']['id']

    try:
        layout = json.loads(event['body'])
        layout['layoutId'] = layout_id
        layout['version'] = layout.get('version', 1) + 1

        layouts_table.put_item(Item=layout)

        return {
            'statusCode': 200,
            'body': json.dumps({'success': True})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def delete(event, context):
    """Delete layout"""
    layout_id = event['pathParameters']['id']

    try:
        layouts_table.delete_item(
            Key={'layoutId': layout_id, 'version': 1}
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'success': True})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'error': str(e)})
        }
