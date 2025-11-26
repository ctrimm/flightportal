"""
Lambda authorizers for API Gateway
"""
import os
import hmac

def device(event, context):
    """Authorize device requests"""
    token = event.get('headers', {}).get('authorization', '').replace('Bearer ', '')
    device_key = os.environ['DEVICE_API_KEY']
    admin_key = os.environ['ADMIN_API_KEY']

    # Allow both device and admin keys
    is_authorized = hmac.compare_digest(token, device_key) or hmac.compare_digest(token, admin_key)

    if is_authorized:
        return {
            'isAuthorized': True,
            'context': {
                'role': 'admin' if hmac.compare_digest(token, admin_key) else 'device'
            }
        }

    return {'isAuthorized': False}

def admin(event, context):
    """Authorize admin requests"""
    token = event.get('headers', {}).get('authorization', '').replace('Bearer ', '')
    admin_key = os.environ['ADMIN_API_KEY']

    if hmac.compare_digest(token, admin_key):
        return {
            'isAuthorized': True,
            'context': {'role': 'admin'}
        }

    return {'isAuthorized': False}
