import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Pact Pals — Grow Together',
  description: 'A friendship-first fitness quest where every workout helps your shared pal hatch.',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: `${process.env.NEXT_PUBLIC_BASE_PATH || ''}/icon-light-32x32.png`,
        media: '(prefers-color-scheme: light)',
      },
      {
        url: `${process.env.NEXT_PUBLIC_BASE_PATH || ''}/icon-dark-32x32.png`,
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: `${process.env.NEXT_PUBLIC_BASE_PATH || ''}/icon.svg`,
        type: 'image/svg+xml',
      },
    ],
    apple: `${process.env.NEXT_PUBLIC_BASE_PATH || ''}/apple-icon.png`,
  },
}

export const viewport: Viewport = {
  colorScheme: 'light dark',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
