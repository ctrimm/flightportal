import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Flight Portal - Real-Time Flight Tracking Display',
  description: 'Professional LED display for live flight tracking. Monitor aircraft in real-time with our sleek MatrixPortal-powered device.',
  keywords: 'flight tracking, LED display, aviation, real-time flights, MatrixPortal',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
