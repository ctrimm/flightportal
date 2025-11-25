# Flight Portal Marketing Site

Professional marketing website for Flight Portal - a real-time flight tracking LED display.

## Features

- **Modern Design**: Clean, professional interface with aviation-themed visuals
- **Stripe Integration**: Secure checkout for $149 USD product
- **Responsive**: Mobile-first design that works on all devices
- **Performance**: Built with Next.js 14 and optimized for speed
- **SEO Ready**: Metadata and semantic HTML for search engines
- **AWS Deployment**: Deployed via SST to S3 + CloudFront

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Payments**: Stripe
- **Language**: TypeScript
- **Deployment**: SST (Serverless Stack) to AWS

## Deployment

This site is deployed as part of the SST backend stack. See `../sst-backend/` for deployment.

### SST Deployment (Recommended)

The marketing site is automatically deployed when you deploy the SST backend:

```bash
cd ../sst-backend
npm install
npm run deploy
```

SST will:
- Build the Next.js site
- Deploy to S3 + CloudFront
- Inject environment variables
- Output the site URL

### Local Development

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Configure Environment Variables**:

   For local testing, create `.env.local`:
   ```bash
   STRIPE_SECRET_KEY=sk_test_your_test_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key
   STRIPE_PRICE_ID=price_your_test_price_id
   ```

3. **Run Development Server**:
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000)

## Stripe Configuration

### Creating the Product

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/products)
2. Click "Add Product"
3. Set:
   - **Name**: Flight Portal Device
   - **Description**: Professional real-time flight tracking LED display
   - **Pricing**: One-time payment, $149 USD
4. Click "Save product"
5. Copy the **Price ID** (starts with `price_`) to your `.env` file

### Test Mode

During development, use test mode:
- Use test API keys (start with `sk_test_` and `pk_test_`)
- Use test card: `4242 4242 4242 4242`
- Any future expiry date and CVC

### Production Mode

Before going live:
1. Set live Stripe keys in `../sst-backend/.env`
2. Configure custom domain in SST (optional)
3. Configure Stripe webhook for production
4. Deploy with `npm run deploy -- --stage prod`
5. Test checkout flow thoroughly

## Environment Variables

All environment variables are managed in the SST backend (`../sst-backend/.env`):

```bash
# In sst-backend/.env
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_PRICE_ID=price_your_live_price_id
```

SST automatically injects these into the Next.js site during deployment.

## Customization

### Colors

Edit `tailwind.config.js` to customize the aviation color scheme:
```js
colors: {
  'aviation-blue': '#1e40af',
  'aviation-sky': '#3b82f6',
  'aviation-dark': '#0f172a',
  'aviation-light': '#e0f2fe',
}
```

### Content

Main content is in `app/page.tsx`. Sections include:
- Hero
- Features
- Technical Specifications
- Pricing
- FAQ
- Footer

### Components

Reusable components in `components/`:
- `FlightPath.tsx` - Animated flight path background
- `FeatureCard.tsx` - Feature showcase cards
- `TechSpec.tsx` - Technical specification rows
- `CheckoutButton.tsx` - Stripe checkout button

## Support

For questions or issues, contact support@flightportal.com

## License

MIT License - see main Flight Portal repository
