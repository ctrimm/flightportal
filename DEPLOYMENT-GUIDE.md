# Flight Portal Deployment Guide

This guide covers deploying both the SST serverless backend and the Next.js marketing website.

## Overview

Your Flight Portal system now has three main components:

1. **Device Firmware** (`code_v3_secure.py`) - CircuitPython code for MatrixPortal M4
2. **SST Backend** (`sst-backend/`) - AWS serverless API for OTA updates, config management, and orders
3. **Marketing Site** (`marketing-site/`) - Next.js website with Stripe checkout (deployed via SST)

## Prerequisites

- AWS Account
- Stripe Account
- Node.js 18+ installed
- AWS CLI configured
- Domain name (optional, for production)

---

## Part 1: Deploy SST Backend to AWS

### 1.1 Install Dependencies

```bash
cd sst-backend
npm install
```

### 1.2 Configure Environment Variables

Create `.env` file in `sst-backend/`:

```bash
# API Keys (generate secure random strings)
DEVICE_API_KEY=device_<generate-random-64-char-string>
ADMIN_API_KEY=admin_<generate-random-64-char-string>

# Firmware Signing (generate secure random string)
FIRMWARE_SIGNING_KEY=<generate-random-64-char-string>

# Stripe (for both API and marketing site)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PRICE_ID=price_your_price_id

# S3 Buckets (will be created by SST)
FIRMWARE_BUCKET=flight-portal-firmware
BACKUP_BUCKET=flight-portal-backups

# Optional: Custom domain for production
# DOMAIN=flightportal.com
```

**Generate secure keys:**

```bash
# On macOS/Linux
openssl rand -hex 32

# Or using Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 1.3 Configure Stripe Product First

Before deploying, create your Stripe product:

1. Go to [Stripe Dashboard > Products](https://dashboard.stripe.com/products)
2. Click "Add Product"
3. Set:
   - **Name**: Flight Portal Device
   - **Description**: Professional real-time flight tracking LED display
   - **Pricing**: One-time payment, $149 USD
4. Click "Save product"
5. Copy the **Price ID** (starts with `price_`) and add it to `.env`

### 1.4 Deploy to AWS

This single command deploys EVERYTHING (backend API + marketing site):

```bash
# Deploy to dev stage
npm run dev

# Or deploy to production
npm run deploy -- --stage prod
```

SST will create:
- **Backend**: 5 DynamoDB tables, 2 S3 buckets, API Gateway, 7 Lambda functions
- **Marketing Site**: Next.js build deployed to S3 + CloudFront CDN
- All environment variables automatically injected

### 1.5 Note Your URLs

After deployment, SST will output:

```
API: https://abc123.execute-api.us-east-1.amazonaws.com
SiteUrl: https://d111111abcdef8.cloudfront.net
```

Save these URLs:
- **API**: For device configuration
- **SiteUrl**: Your marketing website (live and ready!)

### 1.6 Set Up Stripe Webhook

1. Go to [Stripe Dashboard > Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Enter webhook URL: `https://your-api-url.com/api/stripe/webhook`
4. Select events:
   - `checkout.session.completed`
5. Copy the webhook signing secret to `.env` as `STRIPE_WEBHOOK_SECRET`
6. Redeploy: `npm run deploy`

---

## Part 2: Test Marketing Site Locally (Optional)

If you want to test the marketing site locally before deploying:

```bash
cd marketing-site
npm install

# Create .env.local for local testing
cat > .env.local <<EOF
STRIPE_SECRET_KEY=sk_test_your_test_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
STRIPE_PRICE_ID=price_your_test_price_id
EOF

# Run dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

Test checkout with Stripe test card:
- Card: `4242 4242 4242 4242`
- Expiry: Any future date
- CVC: Any 3 digits

**Note**: The production site is already deployed via SST. This is just for local testing!

---

## Part 3: Configure Devices

### 3.1 Update Device Configuration

In your device's `settings.toml` or web interface, set:

```toml
[wifi]
ssid = "YourWiFi"
password = "YourPassword"

[api]
base_url = "https://your-api-url.execute-api.us-east-1.amazonaws.com"
api_key = "device_your-device-api-key"

[location]
lat = 40.7128
lon = -74.0060
radius = 50
```

### 3.2 Upload Initial Firmware

Upload `code_v3_secure.py` as initial firmware:

```bash
# Using AWS CLI
aws s3 cp code_v3_secure.py s3://your-firmware-bucket/firmware/latest.py

# Or use the web interface (if deployed)
# Upload through /admin/firmware endpoint
```

### 3.3 Test Device Connection

Power on your device and verify:
1. Device connects to WiFi
2. Device authenticates with API
3. Device fetches configuration
4. Device displays flight data
5. Device checks for firmware updates

---

## Part 4: Production Checklist

### Security

- [ ] Replace all test API keys with production keys
- [ ] Use strong, randomly generated API keys (64+ characters)
- [ ] Enable AWS WAF on API Gateway (optional)
- [ ] Set up CloudWatch alarms for API errors
- [ ] Enable S3 bucket versioning and encryption
- [ ] Restrict API Gateway to HTTPS only
- [ ] Configure CORS properly in API Gateway

### Stripe

- [ ] Switch from test mode to live mode
- [ ] Update all Stripe keys to live keys
- [ ] Set up Stripe webhook for production API
- [ ] Configure product fulfillment process
- [ ] Set up email notifications for orders
- [ ] Test full checkout flow with real card

### Monitoring

- [ ] Set up CloudWatch dashboards
- [ ] Configure Lambda error alerts
- [ ] Monitor DynamoDB capacity
- [ ] Track S3 storage costs
- [ ] Set up API Gateway throttling
- [ ] Enable AWS X-Ray tracing (optional)

### Domain & DNS

- [ ] Purchase domain (e.g., flightportal.com)
- [ ] Configure DNS in Route 53 or your provider
- [ ] Add custom domain to API Gateway (in API.ts stack)
- [ ] Add custom domain to marketing site (in Web.ts stack)
- [ ] Set up SSL certificates (automatic with AWS Certificate Manager)

### Device Fleet Management

- [ ] Create device provisioning workflow
- [ ] Set up device registration process
- [ ] Generate unique API keys per device (optional)
- [ ] Create device management dashboard
- [ ] Plan firmware rollout strategy

---

## Cost Estimates (AWS)

### Small Scale (100 devices, monthly)

- API Gateway: ~$3.50 (1M requests)
- Lambda: ~$0.20 (1M requests, 128MB)
- DynamoDB: ~$1.25 (on-demand)
- S3: ~$0.30 (10GB storage + transfers)
- CloudFront (marketing site): ~$1.00 (1GB transfer)
- **Total: ~$6.25/month**

### Medium Scale (1,000 devices, monthly)

- API Gateway: ~$35 (10M requests)
- Lambda: ~$2.00 (10M requests)
- DynamoDB: ~$12.50 (on-demand)
- S3: ~$2.30 (50GB storage + transfers)
- CloudFront: ~$8.50 (100GB transfer)
- **Total: ~$60.30/month**

### Large Scale (10,000 devices, monthly)

- API Gateway: ~$350 (100M requests)
- Lambda: ~$20 (100M requests)
- DynamoDB: ~$125 (on-demand)
- S3: ~$23 (500GB storage + transfers)
- CloudFront: ~$85 (1TB transfer)
- **Total: ~$603/month**

*All infrastructure hosted on AWS. No third-party hosting fees.*

---

## Stripe Fees

- **Per transaction**: 2.9% + $0.30
- **$149 product**: $4.62 per sale
- **Net revenue**: $144.38 per sale

---

## Troubleshooting

### SST Deployment Fails

```bash
# Clear SST cache
rm -rf .sst

# Re-run deployment
npm run deploy
```

### Lambda Can't Access DynamoDB

Check IAM permissions in `stacks/API.ts`:
```typescript
bind: [configTable, layoutsTable, devicesTable, firmwareTable, ordersTable]
```

### Stripe Webhook Not Working

1. Check webhook secret matches `.env`
2. Verify webhook URL is correct
3. Check Lambda logs in CloudWatch
4. Test with Stripe CLI: `stripe listen --forward-to localhost:3000/api/stripe/webhook`

### Device Can't Connect to API

1. Verify API URL is correct
2. Check device API key matches backend
3. Verify API Gateway authorizer is working
4. Check CloudWatch logs for Lambda authorizer

### Marketing Site Checkout Fails

1. Verify Stripe keys are correct
2. Check browser console for errors
3. Verify Price ID is correct
4. Test with Stripe test card first

---

## Next Steps

1. **Set up Stripe** product and get Price ID
2. **Configure environment variables** in `sst-backend/.env`
3. **Deploy everything with SST**: `cd sst-backend && npm run deploy`
4. **Configure Stripe webhook** with your API URL
5. **Test marketing site** at the CloudFront URL
6. **Configure first device** with API credentials
7. **Test end-to-end flow**: Order → Device setup → OTA update → Firmware update
8. **Plan device fulfillment** workflow for customer orders

---

## Support Resources

- **SST Documentation**: https://docs.sst.dev
- **Stripe Documentation**: https://stripe.com/docs
- **Next.js Documentation**: https://nextjs.org/docs
- **AWS Lambda**: https://docs.aws.amazon.com/lambda
- **CircuitPython**: https://circuitpython.org

---

## Architecture Diagram

```
┌─────────────────┐
│   Customer      │
│   Browser       │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│         CloudFront CDN                    │
│    (Marketing Site - Next.js on S3)      │
└────────┬──────────────┬──────────────────┘
         │              │
         │              └──────────────────┐
         ▼                                 │
┌─────────────────┐                        │
│   Stripe        │                        │
│   Checkout      │                        │
└─────────────────┘                        │
         │                                 │
         │ (webhook)                       │
         ▼                                 ▼
┌─────────────────────────────────────────────┐
│         AWS API Gateway                      │
│         (Lambda Authorizer)                  │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         Lambda Functions                     │
│  • Config • Layouts • Firmware               │
│  • Orders • Stripe Webhooks • Fields         │
└────┬──────────┬──────────┬─────────────────┘
     │          │          │
     ▼          ▼          ▼
┌─────────┐ ┌────────┐ ┌────────┐
│DynamoDB │ │   S3   │ │ Stripe │
│ Tables  │ │Firmware│ │  API   │
└─────────┘ └────────┘ └────────┘
     ▲          ▲
     │          │
     └──────────┴──────────┐
                           │
                    ┌──────┴─────┐
                    │  Flight    │
                    │  Portal    │
                    │  Device    │
                    │ (MatrixM4) │
                    └────────────┘

All deployed via SST to AWS
```

---

Good luck with your deployment! 🚀✈️
