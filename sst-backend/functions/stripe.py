"""
Stripe webhook handler
"""
import json
import os
import boto3
import stripe
from datetime import datetime

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ['SST_Table_tableName_orders'])
devices_table = dynamodb.Table(os.environ['SST_Table_tableName_devices'])

def webhook(event, context):
    """Handle Stripe webhooks"""
    payload = event['body']
    sig_header = event['headers'].get('stripe-signature')

    try:
        # Verify webhook signature
        stripe_event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError:
        return {'statusCode': 400}
    except stripe.error.SignatureVerificationError:
        return {'statusCode': 400}

    # Handle the event
    if stripe_event['type'] == 'checkout.session.completed':
        session = stripe_event['data']['object']

        # Store order
        order_id = session['id']
        customer_email = session['customer_details']['email']
        quantity = int(session['metadata'].get('quantity', 1))

        orders_table.put_item(Item={
            'orderId': order_id,
            'customerId': customer_email,
            'created': int(datetime.now().timestamp()),
            'amount': session['amount_total'],
            'quantity': quantity,
            'status': 'paid',
            'devices_allocated': False
        })

        # TODO: Send device setup email to customer
        # TODO: Generate device IDs and API keys
        print(f"Order completed: {order_id} for {customer_email}")

    return {'statusCode': 200}
