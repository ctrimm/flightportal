'use client'

import { motion } from 'framer-motion'

interface TechSpecProps {
  label: string
  value: string
  index: number
}

export default function TechSpec({ label, value, index }: TechSpecProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      whileInView={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      viewport={{ once: true }}
      className="flex justify-between items-center py-4 border-b border-gray-200 last:border-b-0"
    >
      <span className="text-gray-600 font-medium">{label}</span>
      <span className="text-aviation-dark font-bold">{value}</span>
    </motion.div>
  )
}
