import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/atoms/Navbar";

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
      <body className={`${geistSans.variable} ${geist.variable} antialiased bg-black`}>
        <Navbar />
        <div>
          {children}
        </div>
      </body>
    </html>
  );
}
