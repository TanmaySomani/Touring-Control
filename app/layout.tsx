import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Touring Control · Commercial Inventory Intelligence",
  description: "Flight inventory, release risk and demand forecasting for touring operations. An independent commercial analytics portfolio project.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
