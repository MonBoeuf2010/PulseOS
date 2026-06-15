/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Static export so Capacitor can bundle the web build as a native shell (out/).
  output: "export",
  // next/image optimization needs a server; disable it for the static export.
  images: { unoptimized: true },
};

export default nextConfig;
