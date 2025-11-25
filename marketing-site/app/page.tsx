'use client'

import {
  Plane,
  Wifi,
  Zap,
  Shield,
  Cloud,
  Smartphone,
  Monitor,
  Radio,
  MapPin,
  Settings
} from 'lucide-react'
import FlightPath from '@/components/FlightPath'
import FeatureCard from '@/components/FeatureCard'
import TechSpec from '@/components/TechSpec'
import CheckoutButton from '@/components/CheckoutButton'

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-aviation-dark via-aviation-blue to-aviation-sky">
        <FlightPath />

        <div className="relative z-10 max-w-6xl mx-auto px-6 py-24 text-center">
          <div className="mb-8 inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20">
            <Plane className="w-5 h-5 text-white" />
            <span className="text-white text-sm font-medium">Professional Flight Tracking Display</span>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Monitor the Skies
            <br />
            <span className="bg-gradient-to-r from-blue-200 to-cyan-200 bg-clip-text text-transparent">
              In Real-Time
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-blue-100 mb-12 max-w-3xl mx-auto leading-relaxed">
            Transform any space into an aviation command center. Track live flights with our sleek LED display powered by cutting-edge technology.
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
            <CheckoutButton />
            <a
              href="#features"
              className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold text-white border-2 border-white rounded-full hover:bg-white hover:text-aviation-blue transition-all duration-300"
            >
              Learn More
            </a>
          </div>

          <div className="mt-16 grid grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">64×32</div>
              <div className="text-blue-200 text-sm">LED Matrix</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">WiFi</div>
              <div className="text-blue-200 text-sm">Connected</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">OTA</div>
              <div className="text-blue-200 text-sm">Updates</div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-white/50 rounded-full mt-2"></div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-aviation-dark mb-4">
              Aviation-Grade Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Engineered for aviation enthusiasts, professionals, and anyone fascinated by flight
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={Radio}
              title="Real-Time Flight Data"
              description="Connect to FlightRadar24 API for live aircraft tracking. Monitor flight numbers, airlines, aircraft types, and positions instantly."
              index={0}
            />
            <FeatureCard
              icon={Monitor}
              title="Vibrant LED Display"
              description="Premium 64×32 RGB LED matrix delivers crystal-clear flight information. Perfect visibility in any lighting condition."
              index={1}
            />
            <FeatureCard
              icon={Wifi}
              title="WiFi Connected"
              description="Seamless wireless connectivity keeps your display updated 24/7. Easy setup through our web-based configuration interface."
              index={2}
            />
            <FeatureCard
              icon={Settings}
              title="Customizable Layouts"
              description="Choose from multiple display layouts or create your own. Show flight numbers, routes, altitude, speed, and more."
              index={3}
            />
            <FeatureCard
              icon={Cloud}
              title="Over-the-Air Updates"
              description="Automatic firmware updates delivered wirelessly. New features and improvements without manual intervention."
              index={4}
            />
            <FeatureCard
              icon={Shield}
              title="Enterprise Security"
              description="Military-grade encryption, HTTPS communication, and code-signed firmware. Your device, your network, secured."
              index={5}
            />
          </div>
        </div>
      </section>

      {/* Technical Specifications */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-aviation-dark mb-6">
                Built on Professional Hardware
              </h2>
              <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                Flight Portal uses the Adafruit MatrixPortal M4, a powerful microcontroller specifically designed for driving LED matrices. Combined with our custom CircuitPython firmware, you get a robust, reliable flight tracking solution.
              </p>

              <div className="bg-gray-50 rounded-xl p-8 border border-gray-200">
                <TechSpec label="Controller" value="MatrixPortal M4" index={0} />
                <TechSpec label="Display" value="64×32 RGB LED (P4)" index={1} />
                <TechSpec label="Connectivity" value="WiFi 802.11 b/g/n" index={2} />
                <TechSpec label="Firmware" value="CircuitPython 9.x" index={3} />
                <TechSpec label="Power" value="5V USB-C" index={4} />
                <TechSpec label="Data Source" value="FlightRadar24 API" index={5} />
                <TechSpec label="Updates" value="OTA (Over-the-Air)" index={6} />
                <TechSpec label="Security" value="HTTPS + Code Signing" index={7} />
              </div>
            </div>

            <div className="bg-gradient-aviation rounded-2xl p-12 text-white shadow-2xl">
              <div className="mb-8">
                <Smartphone className="w-16 h-16 mb-4 opacity-80" />
                <h3 className="text-3xl font-bold mb-4">Web-Based Configuration</h3>
                <p className="text-blue-100 leading-relaxed">
                  Configure your Flight Portal through an intuitive web interface. Set your location, choose layouts, customize displayed fields, and manage WiFi settings—all from your browser.
                </p>
              </div>

              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 mt-1 flex-shrink-0" />
                  <div>
                    <div className="font-semibold">Location-Based Tracking</div>
                    <div className="text-sm text-blue-100">Track flights within your customizable radius</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Zap className="w-5 h-5 mt-1 flex-shrink-0" />
                  <div>
                    <div className="font-semibold">Dynamic Field Selection</div>
                    <div className="text-sm text-blue-100">Display altitude, speed, aircraft type, and more</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Settings className="w-5 h-5 mt-1 flex-shrink-0" />
                  <div>
                    <div className="font-semibold">Multiple Layouts</div>
                    <div className="text-sm text-blue-100">Switch between information density levels</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 bg-gradient-to-br from-gray-900 via-aviation-dark to-aviation-blue relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '40px 40px'
          }}></div>
        </div>

        <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready for Takeoff?
          </h2>
          <p className="text-xl text-blue-200 mb-12 max-w-2xl mx-auto">
            Get your Flight Portal device today and start tracking flights in real-time. Everything you need is included.
          </p>

          <div className="bg-white rounded-3xl p-12 shadow-2xl max-w-lg mx-auto">
            <div className="mb-8">
              <div className="text-5xl font-bold text-aviation-dark mb-2">$149</div>
              <div className="text-gray-600">One-time purchase</div>
            </div>

            <div className="space-y-4 mb-10 text-left">
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                  <div className="w-2 h-2 rounded-full bg-green-600"></div>
                </div>
                <span className="text-gray-700">MatrixPortal M4 Controller</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                  <div className="w-2 h-2 rounded-full bg-green-600"></div>
                </div>
                <span className="text-gray-700">64×32 RGB LED Matrix Display</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                  <div className="w-2 h-2 rounded-full bg-green-600"></div>
                </div>
                <span className="text-gray-700">Pre-loaded Flight Portal Firmware</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                  <div className="w-2 h-2 rounded-full bg-green-600"></div>
                </div>
                <span className="text-gray-700">Web Configuration Interface</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                  <div className="w-2 h-2 rounded-full bg-green-600"></div>
                </div>
                <span className="text-gray-700">Lifetime OTA Firmware Updates</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                  <div className="w-2 h-2 rounded-full bg-green-600"></div>
                </div>
                <span className="text-gray-700">Setup Guide & Documentation</span>
              </div>
            </div>

            <CheckoutButton />

            <p className="text-sm text-gray-500 mt-6">
              Ships within 5-7 business days. 30-day money-back guarantee.
            </p>
          </div>

          <div className="mt-12 text-blue-200 text-sm">
            <p>Secure checkout powered by Stripe</p>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-24 bg-white">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-4xl font-bold text-aviation-dark mb-12 text-center">
            Frequently Asked Questions
          </h2>

          <div className="space-y-6">
            <details className="group bg-gray-50 rounded-lg p-6 cursor-pointer">
              <summary className="font-semibold text-lg text-aviation-dark flex justify-between items-center">
                Do I need a subscription for flight data?
                <span className="text-aviation-sky group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <p className="mt-4 text-gray-600 leading-relaxed">
                No subscription required! Flight Portal uses the publicly available FlightRadar24 API. Simply connect to WiFi and start tracking flights immediately.
              </p>
            </details>

            <details className="group bg-gray-50 rounded-lg p-6 cursor-pointer">
              <summary className="font-semibold text-lg text-aviation-dark flex justify-between items-center">
                How do I set up the device?
                <span className="text-aviation-sky group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <p className="mt-4 text-gray-600 leading-relaxed">
                Simply plug in the device via USB-C, connect to your WiFi network through the web interface, set your location, and you're ready to go. Setup takes less than 5 minutes.
              </p>
            </details>

            <details className="group bg-gray-50 rounded-lg p-6 cursor-pointer">
              <summary className="font-semibold text-lg text-aviation-dark flex justify-between items-center">
                Can I customize what information is displayed?
                <span className="text-aviation-sky group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <p className="mt-4 text-gray-600 leading-relaxed">
                Absolutely! Choose from multiple layouts and customize which fields to display: flight number, airline, aircraft type, altitude, speed, route codes, and more. All configurable through the web interface.
              </p>
            </details>

            <details className="group bg-gray-50 rounded-lg p-6 cursor-pointer">
              <summary className="font-semibold text-lg text-aviation-dark flex justify-between items-center">
                How are firmware updates delivered?
                <span className="text-aviation-sky group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <p className="mt-4 text-gray-600 leading-relaxed">
                Updates are delivered over-the-air (OTA) automatically. When a new firmware version is available, your device downloads and installs it seamlessly. All updates are code-signed for security.
              </p>
            </details>

            <details className="group bg-gray-50 rounded-lg p-6 cursor-pointer">
              <summary className="font-semibold text-lg text-aviation-dark flex justify-between items-center">
                What's your return policy?
                <span className="text-aviation-sky group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <p className="mt-4 text-gray-600 leading-relaxed">
                We offer a 30-day money-back guarantee. If you're not completely satisfied with your Flight Portal, return it for a full refund, no questions asked.
              </p>
            </details>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-aviation-dark text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Plane className="w-6 h-6" />
                <span className="text-xl font-bold">Flight Portal</span>
              </div>
              <p className="text-blue-200">
                Professional real-time flight tracking display for aviation enthusiasts.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-blue-200">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-blue-200">
                <li><a href="#" className="hover:text-white transition-colors">Setup Guide</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">FAQ</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-blue-900 pt-8 text-center text-blue-200 text-sm">
            <p>&copy; 2024 Flight Portal. All rights reserved. Built with ✈️ for aviation enthusiasts.</p>
            <p className="mt-2">Licensed under MIT License • Powered by FlightRadar24 API</p>
          </div>
        </div>
      </footer>
    </main>
  )
}
