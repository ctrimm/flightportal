'use client'

import { useEffect, useState } from 'react'
import { Plane } from 'lucide-react'

export default function FlightPath() {
  const [planes, setPlanes] = useState<{ id: number; delay: number; duration: number }[]>([])

  useEffect(() => {
    // Generate random flight paths
    const newPlanes = Array.from({ length: 3 }, (_, i) => ({
      id: i,
      delay: i * 7,
      duration: 15 + Math.random() * 10,
    }))
    setPlanes(newPlanes)
  }, [])

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
      {planes.map((plane) => (
        <div
          key={plane.id}
          className="absolute"
          style={{
            top: `${20 + plane.id * 30}%`,
            animationDelay: `${plane.delay}s`,
            animationDuration: `${plane.duration}s`,
          }}
        >
          <Plane className="w-6 h-6 text-aviation-sky animate-flight" />
        </div>
      ))}
    </div>
  )
}
