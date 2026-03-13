import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Sans } from "next/font/google";

import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
});

const plex = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-body",
});

export const metadata: Metadata = {
  title: "Model Validation Workbench",
  description:
    "Artifact-first bank model validation with explicit coverage boundaries, staged analyst workflows, and bank-facing reports.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${fraunces.variable} ${plex.variable}`}>{children}</body>
    </html>
  );
}
