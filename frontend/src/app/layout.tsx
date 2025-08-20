import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/atoms/Navbar";
import { Toaster } from "@/components/ui/sonner";
import Footer from "@/components/atoms/Footer";

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist",
});

export const metadata: Metadata = {
  title: "Cinéma & Inégalités",
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
      <body
        className={`${geistSans.variable} ${geist.variable} antialiased bg-red min-h-screen h-full`}
        style={{
          background: '#0B0C0F'
        }}
        suppressHydrationWarning
      >
        <Navbar>{children}</Navbar>
        <Footer />
        <Toaster />
      </body>
    </html>
  );
}
