/** @type {import('next').NextConfig} */
const nextConfig = {
  // Produce a minimal, self-contained server bundle for the Docker image.
  output: "standalone",
  reactStrictMode: true,
};

export default nextConfig;
