import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/atoms/Navbar";
import { Toaster } from "@/components/ui/sonner";
import Footer from "@/components/atoms/Footer";
import { SearchProvider } from "@/contexts/SearchContext";
import Script from "next/script";

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist",
});

export const metadata: Metadata = {
  title: "CinéStats 50/50",
  description: "Explorez les inégalités dans l'industrie cinématographique",
  authors: [{ name: "Data4Good" }],
  keywords: ["cinéma", "inégalités", "data", "analyse", "statistiques"],
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
