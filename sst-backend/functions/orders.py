"""
Order management and Stripe integration
"""
import json
import os
import boto3
import stripe
from datetime import datetime

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ['SST_Table_tableName_orders'])

def create(event, context):
    """Create Stripe checkout session"""
    try:
        data = json.loads(event['body'])
        quantity = data.get('quantity', 1)

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': os.environ['STRIPE_PRICE_ID'],  # $149 USD product
                'quantity': quantity,
            }],
            mode='payment',
            success_url=data.get('success_url', 'https://flightportal.com/success'),
            cancel_url=data.get('cancel_url', 'https://flightportal.com'),
            metadata={
                'product': 'flight_portal_device',
                'quantity': quantity
            }
        )

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'sessionId': session.id,
                'url': session.url
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'error': str(e)})
        }
