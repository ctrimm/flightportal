/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'aviation-blue': '#1e40af',
        'aviation-sky': '#3b82f6',
        'aviation-dark': '#0f172a',
        'aviation-light': '#e0f2fe',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-aviation': 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
      },
    },
  },
  plugins: [],
}
