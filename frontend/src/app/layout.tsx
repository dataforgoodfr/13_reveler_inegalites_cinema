import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/atoms/Navbar";
import { Toaster } from "@/components/ui/sonner";
import Footer from "@/components/atoms/Footer";
import { SearchProvider } from "@/contexts/SearchContext";
import Script from "next/script";
import {
  SITE_NAME,
  SITE_DESCRIPTION,
  DEFAULT_KEYWORDS,
} from "@/lib/seo";

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist",
});

export const metadata: Metadata = {
  title: {
    default: `${SITE_NAME} — Inégalités de parité dans le cinéma`,
    template: `%s | ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  authors: [{ name: "Data4Good" }, { name: "Collectif 50/50" }],
  keywords: DEFAULT_KEYWORDS,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html className="min-h-screen h-full" lang="fr">
      <head>
        <Script
          defer
          src="https://cloud.umami.is/script.js"
          data-website-id="996668f1-b9bd-4892-974d-b9a0bb145082"
        />
      </head>
      <body
        className={`${geistSans.variable} ${geist.variable} antialiased bg-red min-h-screen h-full`}
        style={{
          background: "#0B0C0F",
        }}
        suppressHydrationWarning
      >
        <SearchProvider>
          <Navbar>{children}</Navbar>
          <Footer />
          <Toaster />
        </SearchProvider>
      </body>
    </html>
  );
}
