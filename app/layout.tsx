import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Orange Test – Find Cloudflare-hosted subdomains",
  description:
    "Passive subdomain discovery and Cloudflare IP classification. Use only on domains you own or are authorized to assess.",
  robots: "noindex, nofollow",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
