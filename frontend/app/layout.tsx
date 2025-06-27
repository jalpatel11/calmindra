import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
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
  title: "Calmindra - Your Mental Health Companion",
  description: "A compassionate AI-powered mental health chatbot providing emotional support, coping strategies, and a safe space to explore your thoughts and feelings.",
  keywords: ["mental health", "emotional support", "AI chatbot", "wellness", "therapy", "mindfulness"],
  authors: [{ name: "Calmindra Team" }],
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
  openGraph: {
    title: "Calmindra - Mental Health Companion",
    description: "Your compassionate AI companion for mental health support",
    type: "website",
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Calmindra - Mental Health Companion',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Calmindra - Mental Health Companion',
    description: 'Your compassionate AI companion for mental health support',
    images: ['/og-image.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
