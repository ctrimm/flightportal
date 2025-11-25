# Flight Portal Marketing Site

Professional marketing website for Flight Portal - a real-time flight tracking LED display.

## Features

- **Modern Design**: Clean, professional interface with aviation-themed visuals
- **Stripe Integration**: Secure checkout for $149 USD product
- **Responsive**: Mobile-first design that works on all devices
- **Performance**: Built with Next.js 14 and optimized for speed
- **SEO Ready**: Metadata and semantic HTML for search engines

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Payments**: Stripe
- **Language**: TypeScript

## Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Stripe keys:
   - Get your Stripe keys from https://dashboard.stripe.com/apikeys
   - Create a product in Stripe Dashboard for $149
   - Copy the Price ID to `STRIPE_PRICE_ID`

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
1. Switch to live API keys in `.env`
2. Update `NEXT_PUBLIC_BASE_URL` to your production domain
3. Configure Stripe webhook for production (optional)
4. Test checkout flow thoroughly

## Deployment

### Deploy to Vercel

1. Push code to GitHub
2. Import to [Vercel](https://vercel.com)
3. Add environment variables in Vercel dashboard
4. Deploy

### Environment Variables in Production

Set these in your hosting platform:
- `STRIPE_SECRET_KEY` - Live secret key
- `STRIPE_PUBLISHABLE_KEY` - Live publishable key (if needed client-side)
- `STRIPE_PRICE_ID` - Live price ID
- `NEXT_PUBLIC_BASE_URL` - Your production domain

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
