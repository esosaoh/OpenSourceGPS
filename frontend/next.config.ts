import { NextConfig } from 'next'

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://9f5d-208-98-222-98.ngrok-free.app/api/:path*',
      },
    ]
  },
}

export default nextConfig