// import type { NextConfig } from "next";

// const nextConfig: NextConfig = {
//   /* config options here */
// };

// export default nextConfig;
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    allowedDevOrigins: [
      'http://192.168.100.122:3000', // your mobile IP + port
      'http://192.168.43.100:3000',  // your laptop hotspot IP if different
    ],
  },
};

module.exports = nextConfig;
