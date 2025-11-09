import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import { Toaster } from '@/components/ui/toaster';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'ExtraCoin — AI-Powered Trading & Investment Platform',
  description:
    'Trade CFDs in simulation mode or invest with our AI-powered trading engine. Regulated by CMF. Choose your path to financial growth.',
  keywords: [
    'CFD trading',
    'futures',
    'trading simulator',
    'AI trading',
    'backtesting',
    'virtual trading',
  ],
  authors: [{ name: 'ExtraCoin' }],
  icons: {
    icon: '/favicon.ico',
  },
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#2B6EEA',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
