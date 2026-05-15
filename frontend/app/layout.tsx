import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MediShield AI — Intelligent Claims Adjudication",
  description: "Next-generation AI-powered document intake, fraud detection, and claims adjudication pipeline for health insurance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-full flex flex-col relative">
        {/* Animated background orbs */}
        <div className="bg-scene" aria-hidden="true">
          <div className="bg-orb bg-orb-1" />
          <div className="bg-orb bg-orb-2" />
          <div className="bg-orb bg-orb-3" />
          <div className="bg-grid" />
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col flex-1">
          {children}
        </div>
      </body>
    </html>
  );
}
