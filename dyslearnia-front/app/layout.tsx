import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const openDyslexic = localFont({
  src: [
    {
      path: "../public/fonts/OpenDyslexic-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../public/fonts/OpenDyslexic-Bold.woff2",
      weight: "700",
      style: "normal",
    },
    {
      path: "../public/fonts/OpenDyslexic-Italic.woff2",
      weight: "400",
      style: "italic",
    },
    {
      path: "../public/fonts/OpenDyslexic-BoldItalic.woff2",
      weight: "700",
      style: "italic",
    },
  ],
  variable: "--font-open-dyslexic",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Dyslearnia",
  description: "A learning platform designed for students with dyslexia",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${openDyslexic.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
