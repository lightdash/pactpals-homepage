import type { Metadata, Viewport } from "next";
import "./globals.css";
import GoogleAnalytics from "../components/google-analytics";

export const metadata: Metadata = {
  title: "Pact Pals | Grow Together",
  description:
    "A friendship-first fitness quest where every workout helps your shared pal hatch.",
  generator: "v0.app",
  metadataBase: new URL("https://pactpals.com"),
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/icon-32x32.png", sizes: "32x32", type: "image/png" },
    ],
    apple: "/apple-icon.png",
  },
  openGraph: {
    type: "website",
    url: "/",
    siteName: "Pact Pals",
    title: "Pact Pals | Grow Together",
    description:
      "A friendship-first fitness quest where every workout helps your shared pal hatch.",
    images: [
      {
        url: "/og-image.png",
        width: 1024,
        height: 500,
        alt: "Pact Pals — Small steps. Shared adventures.",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Pact Pals | Grow Together",
    description:
      "A friendship-first fitness quest where every workout helps your shared pal hatch.",
    images: ["/og-image.png"],
  },
};

export const viewport: Viewport = {
  colorScheme: "light",
  themeColor: "#f4efe2",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}<GoogleAnalytics /></body>
    </html>
  );
}
