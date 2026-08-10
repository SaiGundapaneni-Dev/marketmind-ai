import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import AuthGuard from "@/components/AuthGuard";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Vestora AI — Investing clarity without the noise",
    template: "%s | Vestora AI",
  },
  description:
    "Vestora AI monitors your portfolio, filters market noise and explains what deserves your attention.",
  applicationName: "Vestora AI",
  keywords: [
    "portfolio intelligence",
    "AI investing copilot",
    "investment portfolio",
    "portfolio monitoring",
    "investment thesis",
  ],
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-[#020817]">
        <AuthGuard>{children}</AuthGuard>
      </body>
    </html>
  );
}
