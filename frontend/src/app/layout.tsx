import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/atoms/Navbar";
import { Toaster } from "@/components/ui/sonner";

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
    <html lang="en">
      <body className={`${geistSans.variable} ${geist.variable} antialiased bg-black`} suppressHydrationWarning>
        <Navbar>
          {children}
        </Navbar>
        <Toaster />
      </body>
    </html>
  );
}
