# AWS Deployment Guide for Commercial Flight Portal

## 🤔 Why You Need Cloud Hosting

Your Flight Portal devices need cloud hosting for:

### 1. **OTA Firmware Updates** (Primary Reason)
- Devices fetch firmware updates from your server
- Must be accessible 24/7 from anywhere
- Customers' devices on their networks need to reach your update server

### 2. **Configuration Management**
- Devices poll for config updates (layouts, settings, WiFi)
- Customer can't access your localhost:3100
- Need persistent, publicly accessible config storage

### 3. **Device Fleet Management**
- Track which devices are online
- Monitor firmware versions across fleet
- Push updates to specific devices or groups

### 4. **Customer Portal** (Optional)
- Let customers configure their own devices
- View device status and logs
- Download firmware manually

---

## 🏗️ Architecture Options for AWS

### Option 1: **SST Serverless** (Recommended - You're Familiar!)

Perfect for your use case - API-based, auto-scaling, pay-per-use.

```
┌─────────────────────────────────────────────────┐
│  Flight Portal Devices (MatrixPortal)          │
│  → Fetch config & firmware via HTTPS           │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  CloudFront (CDN) + API Gateway                 │
│  → HTTPS endpoint                               │
│  → SSL/TLS termination                          │
│  → Custom domain: api.flightportal.com          │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
┌──────────┐          ┌──────────────┐
│ Lambda   │          │ Lambda       │
│ Functions│          │ Functions    │
│          │          │              │
│ • Config │          │ • Firmware   │
│ • Status │          │ • Upload     │
└────┬─────┘          └──────┬───────┘
     │                       │
     ▼                       ▼
┌─────────────┐      ┌──────────────┐
│ DynamoDB    │      │ S3 Bucket    │
│ • Device    │      │ • Firmware   │
│   configs   │      │   files      │
│ • Layouts   │      │ • Signatures │
│ • Settings  │      └──────────────┘
└─────────────┘
```

**SST Structure:**
```typescript
// sst.config.ts
export default {
  config() {
    return {
      name: "flight-portal",
      region: "us-east-1",
    };
  },
  stacks(app) {
    app.stack(function Stack({ stack }) {
      // S3 bucket for firmware storage
      const firmwareBucket = new Bucket(stack, "firmware");

      // DynamoDB for configs
      const configTable = new Table(stack, "config", {
        fields: { deviceId: "string", layoutId: "string" },
        primaryIndex: { partitionKey: "deviceId" },
      });

      // API
      const api = new Api(stack, "api", {
        defaults: {
          function: {
            bind: [firmwareBucket, configTable],
          },
        },
        routes: {
          "GET /api/config": "functions/config.get",
          "PUT /api/config": "functions/config.update",
          "GET /api/firmware/check": "functions/firmware.check",
          "GET /api/firmware/download": "functions/firmware.download",
          "POST /api/firmware/upload": "functions/firmware.upload",
        },
      });

      // Custom domain
      api.attachCustomDomain({
        domainName: "api.flightportal.com",
      });

      stack.addOutputs({
        ApiEndpoint: api.url,
      });
    });
  },
};
```

**Pros:**
- ✅ You're already familiar with SST
- ✅ Auto-scales to millions of requests
- ✅ Pay only for what you use (~$5-20/month for startup)
- ✅ Built-in CDN (CloudFront)
- ✅ Easy deployments: `sst deploy`
- ✅ Great for API-heavy workloads

**Cons:**
- ❌ Flask app needs refactoring to Lambda handlers
- ❌ Cold starts (200-500ms first request)
- ❌ Lambda timeout: 15 min max

**Cost Estimate:**
- 10,000 devices × 12 requests/day = 120K requests/month
- API Gateway: $3.50/million requests = ~$0.42/month
- Lambda: 128MB × 100ms avg = ~$0.50/month
- DynamoDB: On-demand = ~$2-5/month
- S3: 100MB firmware × transfers = ~$1/month
- **Total: ~$5-10/month**

---

### Option 2: **Lightsail** (Simplest - Flask as-is)

Run your Flask app directly, no refactoring needed.

```
┌─────────────────────────────────────────────────┐
│  Flight Portal Devices (MatrixPortal)          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Route 53                                       │
│  → api.flightportal.com                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Lightsail Instance ($5-10/month)               │
│  • Ubuntu 22.04                                 │
│  • Flask app running with Gunicorn              │
│  • Nginx reverse proxy                          │
│  • Let's Encrypt SSL                            │
│  • SQLite or PostgreSQL database                │
└─────────────────────────────────────────────────┘
```

**Setup:**
```bash
# Launch Lightsail instance
# SSH into instance

# Install dependencies
sudo apt update
sudo apt install python3-pip nginx certbot python3-certbot-nginx

# Clone your code
git clone <your-repo>
cd flightportal/web-interface

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Configure Nginx reverse proxy
sudo nano /etc/nginx/sites-available/flightportal
```

**Nginx Config:**
```nginx
server {
    listen 80;
    server_name api.flightportal.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**SSL Setup:**
```bash
sudo certbot --nginx -d api.flightportal.com
```

**Pros:**
- ✅ Use Flask app as-is (no refactoring)
- ✅ Simple to understand and debug
- ✅ SSH access for troubleshooting
- ✅ Predictable pricing ($5-10/month)
- ✅ Can run background tasks

**Cons:**
- ❌ Manual scaling (upgrade instance size)
- ❌ Single point of failure (need backups)
- ❌ You manage OS updates and security

**Cost:**
- $5/month for 512MB RAM instance
- Handles ~100 concurrent devices easily

---

### Option 3: **Hybrid** (Best of Both Worlds)

Serverless API + S3 for firmware, keep Flask for admin.

```
Devices → API Gateway + Lambda → DynamoDB
                                ↓
Firmware downloads → S3 + CloudFront (CDN)
                                ↓
Admin portal → Lightsail/EC2 Flask app
```

**Why Hybrid:**
- Devices use serverless (scales infinitely)
- Firmware served from S3 (fast CDN)
- Admin portal on Lightsail (easier to manage)

---

## 📋 What Each Service Does

### **What You MUST Have:**

| Service | Purpose | Why? |
|---------|---------|------|
| **API Gateway** or **ALB** | HTTPS endpoints | Devices call `/api/config`, `/api/firmware` |
| **Lambda** or **EC2/Lightsail** | Run Flask app | Process requests, generate responses |
| **S3** | Store firmware files | Devices download `.py` files for OTA |
| **DynamoDB** or **RDS** | Store configs | Device settings, layouts, API keys |
| **Route 53** | DNS | `api.flightportal.com` → your infrastructure |
| **Certificate Manager** | SSL/TLS | HTTPS for secure device communication |

### **What's Optional but Recommended:**

| Service | Purpose | Why? |
|---------|---------|------|
| **CloudFront** | CDN | Faster firmware downloads worldwide |
| **CloudWatch** | Logging & monitoring | Track errors, device requests |
| **Secrets Manager** | Store API keys | Better than hardcoding in Lambda |
| **WAF** | Security | Block malicious traffic |
| **Cognito** | User auth | If you add customer login portal |

---

## 🚀 Recommended Path: SST Serverless

Since you're familiar with SST, here's a step-by-step migration:

### Step 1: Convert Flask Routes to Lambda Handlers

Your current Flask route:
```python
@app.route('/api/config', methods=['GET'])
@require_auth('device')
def get_config():
    config = load_json(DEVICE_CONFIG_PATH)
    return jsonify(config)
```

Becomes Lambda handler:
```python
# functions/config.py
import json
import boto3
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CONFIG_TABLE'])

@tracer.capture_lambda_handler
@logger.inject_lambda_context
def get(event, context):
    # Extract device ID from API key (simplified)
    device_id = event['requestContext']['authorizer']['deviceId']

    # Get config from DynamoDB
    response = table.get_item(Key={'deviceId': device_id})
    config = response.get('Item', {})

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(config)
    }
```

### Step 2: Replace JSON Files with DynamoDB

Current: `config/device_config.json`
```json
{
  "wifi": {"ssid": "...", "password": "..."},
  "active_layout": "classic"
}
```

DynamoDB structure:
```
Table: flight-portal-config
Partition Key: deviceId (String)

Item:
{
  "deviceId": "FP-00001",
  "wifi": {"ssid": "...", "password": "..."},
  "active_layout": "classic",
  "lastUpdated": "2025-11-25T10:00:00Z"
}
```

### Step 3: Move Firmware to S3

Current: `web-interface/firmware/code_v3_ota.py`

S3 structure:
```
Bucket: flight-portal-firmware
Key: firmware/3.0.0/code.py
Metadata:
  - x-amz-meta-version: 3.0.0
  - x-amz-meta-signature: abc123...
```

Lambda handler for firmware download:
```python
import boto3
import hmac
import hashlib

s3 = boto3.client('s3')
BUCKET = os.environ['FIRMWARE_BUCKET']
SIGNING_KEY = os.environ['SIGNING_KEY']

def download(event, context):
    version = event['queryStringParameters'].get('version', 'latest')

    # Get firmware from S3
    obj = s3.get_object(Bucket=BUCKET, Key=f'firmware/{version}/code.py')
    firmware_code = obj['Body'].read().decode('utf-8')

    # Sign firmware
    signature = hmac.new(
        SIGNING_KEY.encode(),
        firmware_code.encode(),
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
```

### Step 4: Deploy with SST

```bash
# Initialize SST project
npx create-sst@latest flight-portal
cd flight-portal

# Add your Lambda functions
mkdir -p functions
# Copy converted handlers to functions/

# Deploy
sst deploy --stage prod

# Output:
# ApiEndpoint: https://abc123.execute-api.us-east-1.amazonaws.com
```

### Step 5: Point Devices to New API

Update `code_v3_secure.py`:
```python
CONFIG_SERVER = "abc123.execute-api.us-east-1.amazonaws.com"
# Or with custom domain:
CONFIG_SERVER = "api.flightportal.com"
```

---

## 💰 Cost Breakdown (SST Serverless)

**For 100 devices:**
- API Gateway: 100 × 12 requests/day × 30 days = 36K requests = $0.13
- Lambda: 36K × 100ms × 128MB = $0.06
- DynamoDB: On-demand, 36K reads = $0.05
- S3: 100 firmware downloads/month = $0.02
- **Total: ~$0.30/month**

**For 1,000 devices:**
- API Gateway: ~$1.30
- Lambda: ~$0.60
- DynamoDB: ~$0.50
- S3: ~$0.20
- **Total: ~$3/month**

**For 10,000 devices:**
- API Gateway: ~$13
- Lambda: ~$6
- DynamoDB: ~$5
- S3: ~$2
- **Total: ~$26/month**

Way cheaper than running servers 24/7!

---

## 🎯 Recommendation

**Start with SST Serverless:**
1. Cheap at small scale
2. Scales automatically
3. You're already familiar
4. No server maintenance
5. Built-in monitoring

**Migration path:**
1. Week 1: Convert Flask routes to Lambda handlers
2. Week 2: Set up DynamoDB schemas
3. Week 3: Move firmware to S3
4. Week 4: Deploy and test with test devices
5. Week 5: Point production devices to AWS

---

## 📚 Resources

- **SST Docs**: https://docs.sst.dev
- **AWS Lambda Powertools (Python)**: https://awslabs.github.io/aws-lambda-powertools-python/
- **DynamoDB Best Practices**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html
- **S3 Presigned URLs**: For secure firmware downloads
- **API Gateway Custom Authorizers**: For API key validation

Want me to create the complete SST project structure with all the Lambda handlers converted?
