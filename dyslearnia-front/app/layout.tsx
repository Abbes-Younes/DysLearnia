import type { Metadata } from "next";
import "./globals.css";
import { Geist } from "next/font/google";
import { cn } from "@/lib/utils";
import { AppProvider } from "@/lib/context/app-context";
import { Navbar } from "@/components/navbar";

const geist = Geist({ subsets: ["latin"], variable: "--font-sans" });

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
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <body className="antialiased">
        <AppProvider>
          <Navbar />
          <main className="min-h-screen">{children}</main>
        </AppProvider>
      </body>
    </html>
  );
}
