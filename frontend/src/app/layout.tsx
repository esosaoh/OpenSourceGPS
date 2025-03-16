import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import "./globals.css";

export const metadata: Metadata = {
  title: "GitMentor - AI-Powered Open-Source Contributions",
  description: "Effortlessly contribute to GitHub repositories with AI-driven guidance. GitMentor helps you understand codebases, generate implementation plans, and make meaningful contributions faster.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${GeistSans.className} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}