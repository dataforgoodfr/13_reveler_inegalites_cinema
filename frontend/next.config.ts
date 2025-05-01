import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  distDir: "dist",
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "fr.web.img6.acsta.net",
        port: "",
        pathname: "/img/29/eb/**",
        search: "",
      },
    ],
  },
};

export default nextConfig;
