import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Playfair_Display, Lexend, Geist } from "next/font/google";
import "./globals.css";
import { AppLayout } from "@/components/app-layout";
import { cn } from "@/lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

const playfair = Playfair_Display({
  variable: "--font-serif",
  subsets: ["latin"],
});

const lexend = Lexend({
  variable: "--font-lexend",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Exodus | AI Excel Analysis",
  description: "Professional multi-agent Excel analysis system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={cn("h-full dark", "antialiased", jetbrainsMono.variable, playfair.variable, lexend.variable, "font-sans", geist.variable)}
    >
      <body className="h-full bg-background selection:bg-white/10 selection:text-white">
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}
