'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { CheckCircle, Plane, Mail, Package } from 'lucide-react'
import Link from 'next/link'

export default function SuccessPage() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('session_id')
  const [email, setEmail] = useState<string>('')

  useEffect(() => {
    if (sessionId) {
      // In production, you would verify the session and get customer details
      // For now, we'll just show a success message
    }
  }, [sessionId])

  return (
    <main className="min-h-screen bg-gradient-to-br from-aviation-dark via-aviation-blue to-aviation-sky flex items-center justify-center px-6">
      <div className="max-w-2xl w-full bg-white rounded-3xl shadow-2xl p-12 text-center">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="w-12 h-12 text-green-600" />
        </div>

        <h1 className="text-4xl font-bold text-aviation-dark mb-4">
          Order Confirmed!
        </h1>

        <p className="text-xl text-gray-600 mb-8">
          Thank you for your Flight Portal purchase. Your order has been successfully processed.
        </p>

        {sessionId && (
          <div className="bg-gray-50 rounded-xl p-6 mb-8 text-left">
            <div className="text-sm text-gray-500 mb-2">Order ID</div>
            <div className="font-mono text-sm text-aviation-dark break-all">
              {sessionId}
            </div>
          </div>
        )}

        <div className="space-y-6 mb-10">
          <div className="flex items-start gap-4 text-left">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <Mail className="w-6 h-6 text-aviation-blue" />
            </div>
            <div>
              <h3 className="font-semibold text-aviation-dark mb-1">
                Confirmation Email Sent
              </h3>
              <p className="text-gray-600 text-sm">
                Check your inbox for order details and tracking information.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 text-left">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <Package className="w-6 h-6 text-aviation-blue" />
            </div>
            <div>
              <h3 className="font-semibold text-aviation-dark mb-1">
                Processing Your Order
              </h3>
              <p className="text-gray-600 text-sm">
                Your Flight Portal will ship within 5-7 business days.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 text-left">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <Plane className="w-6 h-6 text-aviation-blue" />
            </div>
            <div>
              <h3 className="font-semibold text-aviation-dark mb-1">
                Setup Guide Coming Soon
              </h3>
              <p className="text-gray-600 text-sm">
                We'll send you a detailed setup guide with your device.
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <Link
            href="/"
            className="inline-block px-8 py-3 bg-gradient-aviation text-white font-semibold rounded-full hover:shadow-xl transition-all duration-300"
          >
            Return to Home
          </Link>

          <p className="text-sm text-gray-500">
            Questions? Contact us at support@flightportal.com
          </p>
        </div>
      </div>
    </main>
  )
}
