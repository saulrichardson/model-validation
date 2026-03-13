import { fileURLToPath } from "node:url";

const rootDirectory = fileURLToPath(new URL("./", import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  turbopack: {
    root: rootDirectory,
  },
};

export default nextConfig;
