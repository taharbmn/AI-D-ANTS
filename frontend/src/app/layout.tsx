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
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-neutral-900 h-screen w-screen flex xl:p-10 p-4`}
        suppressHydrationWarning={true}
      >
        <ChatProvider>
          <DashboardProvider>
            <div className="flex w-full h-full relative">
              <Sidebar />
              <div className="flex-1 xl:ml-0">
                {children}
              </div>
            </div>
          </DashboardProvider>
        </ChatProvider>
      </body>
    </html>
  );
}
