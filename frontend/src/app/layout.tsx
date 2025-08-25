import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/sidebar";
import { ChatProvider } from "@/contexts/ChatContext";
import { DashboardProvider } from "@/contexts/DashboardContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI-D-ANTS",
  description: "AI Data Analysis Tool",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" >
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-neutral-900 h-screen w-screen flex p-10`}
        suppressHydrationWarning={true}
      >
        <ChatProvider>
          <DashboardProvider>
            <Sidebar />
            {children}
          </DashboardProvider>
        </ChatProvider>
      </body>
    </html>
  );
}
