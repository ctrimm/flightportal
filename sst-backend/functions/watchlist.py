"""
Watchlist management for tail number tracking
"""
import json
import os
import time
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
watchlist_table_name = os.environ.get('SST_Table_tableName_watchlist')
watchlist_table = dynamodb.Table(watchlist_table_name) if watchlist_table_name else None


def normalize_tail_number(tail: str) -> str:
    """Normalize tail number format (uppercase, no spaces/dashes)"""
    return tail.upper().replace('-', '').replace(' ', '').strip()


def list(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get watchlist for a device

    Query params:
      - deviceId: Device identifier
    """
    try:
        # Get device ID from query params or use default
        device_id = event.get('queryStringParameters', {}).get('deviceId', 'default')

        # Query watchlist for device
        response = watchlist_table.query(
            KeyConditionExpression='deviceId = :deviceId',
            ExpressionAttributeValues={
                ':deviceId': device_id
            }
        )

        items = response.get('Items', [])

        # Format response
        watchlist = [
            {
                'tailNumber': item['tailNumber'],
                'added': item['added'],
                'nickname': item.get('nickname', ''),
                'notes': item.get('notes', '')
            }
            for item in items
        ]

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'deviceId': device_id,
                'watchlist': watchlist,
                'count': len(watchlist)
            })
        }

    except Exception as e:
        print(f"Error listing watchlist: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }


def add(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Add tail number to watchlist

    POST body:
    {
        "deviceId": "device123",
        "tailNumber": "N12345",
        "nickname": "My Cessna" (optional),
        "notes": "Flight school aircraft" (optional)
    }
    """
    try:
        body = json.loads(event.get('body', '{}'))

        device_id = body.get('deviceId', 'default')
        tail_number = body.get('tailNumber', '').strip()
        nickname = body.get('nickname', '').strip()
        notes = body.get('notes', '').strip()

        if not tail_number:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'tailNumber is required'})
            }

        # Normalize tail number
        tail_normalized = normalize_tail_number(tail_number)

        # Validate tail number format (basic check)
        if len(tail_normalized) < 2 or len(tail_normalized) > 10:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid tail number format'})
            }

        # Add to watchlist
        item = {
            'deviceId': device_id,
            'tailNumber': tail_normalized,
            'added': int(time.time()),
        }

        if nickname:
            item['nickname'] = nickname
        if notes:
            item['notes'] = notes

        watchlist_table.put_item(Item=item)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'tailNumber': tail_normalized,
                'message': f'Added {tail_normalized} to watchlist'
            })
        }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid JSON body'})
        }
    except Exception as e:
        print(f"Error adding to watchlist: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }


def remove(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Remove tail number from watchlist

    Path params:
      - tailNumber: Tail number to remove
    Query params:
      - deviceId: Device identifier
    """
    try:
        # Get tail number from path
        tail_number = event.get('pathParameters', {}).get('tailNumber', '')
        device_id = event.get('queryStringParameters', {}).get('deviceId', 'default')

        if not tail_number:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'tailNumber is required'})
            }

        # Normalize tail number
        tail_normalized = normalize_tail_number(tail_number)

        # Remove from watchlist
        watchlist_table.delete_item(
            Key={
                'deviceId': device_id,
                'tailNumber': tail_normalized
            }
        )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': f'Removed {tail_normalized} from watchlist'
            })
        }

    except Exception as e:
        print(f"Error removing from watchlist: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }
