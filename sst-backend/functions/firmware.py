"""
Firmware OTA update Lambda handlers
"""
import json
import os
import boto3
import hmac
import hashlib

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
firmware_table = dynamodb.Table(os.environ['SST_Table_tableName_firmware'])
firmware_bucket = os.environ['SST_Bucket_bucketName_firmware']
signing_key = os.environ['SIGNING_KEY']

def check(event, context):
    """Check if firmware update available"""
    device_version = event.get('queryStringParameters', {}).get('version', '0.0.0')

    try:
        # Get latest firmware version
        response = firmware_table.scan(
            ProjectionExpression='version, released, changelog, mandatory',
            Limit=10
        )

        versions = sorted(response['Items'], key=lambda x: x['released'], reverse=True)
        if not versions:
            return {
                'statusCode': 200,
                'body': json.dumps({'update_available': False})
            }

        latest = versions[0]
        latest_version = latest['version']

        # Simple version comparison
        device_parts = [int(x) for x in device_version.split('.')]
        latest_parts = [int(x) for x in latest_version.split('.')]

        update_available = (
            latest_parts[0] > device_parts[0] or
            (latest_parts[0] == device_parts[0] and latest_parts[1] > device_parts[1]) or
            (latest_parts[0] == device_parts[0] and latest_parts[1] == device_parts[1] and latest_parts[2] > device_parts[2])
        )

        if update_available:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'update_available': True,
                    'version': latest_version,
                    'changelog': latest.get('changelog', ''),
                    'mandatory': latest.get('mandatory', False),
                    'download_url': f"{event['requestContext']['domainName']}/api/firmware/download"
                })
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'update_available': False, 'current_version': device_version})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def download(event, context):
    """Download firmware with signature"""
    version = event.get('queryStringParameters', {}).get('version', 'latest')

    try:
        # Get firmware file from S3
        key = f"firmware/{version}/code.py"
        response = s3.get_object(Bucket=firmware_bucket, Key=key)
        firmware_code = response['Body'].read().decode('utf-8')

        # Sign firmware
        signature = hmac.new(
            signing_key.encode('utf-8'),
            firmware_code.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/plain',
                'X-Firmware-Signature': signature,
                'X-Firmware-Version': version
            },
            'body': firmware_code
        }
    except s3.exceptions.NoSuchKey:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Firmware not found'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def upload(event, context):
    """Upload new firmware version"""
    try:
        data = json.loads(event['body'])
        version = data['version']
        changelog = data.get('changelog', '')
        code = data['code']
        mandatory = data.get('mandatory', False)

        # Upload to S3
        key = f"firmware/{version}/code.py"
        s3.put_object(
            Bucket=firmware_bucket,
            Key=key,
            Body=code.encode('utf-8'),
            ContentType='text/plain'
        )

        # Store metadata in DynamoDB
        firmware_table.put_item(Item={
            'version': version,
            'released': int(datetime.now().timestamp()),
            'changelog': changelog,
            'mandatory': mandatory,
            's3_key': key
        })

        return {
            'statusCode': 200,
            'body': json.dumps({'success': True, 'message': f'Firmware {version} uploaded'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'error': str(e)})
        }
