import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { SITE_DESCRIPTION, SITE_FULL_NAME } from "@/lib/constants";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "ALIAA — Academia Latinoamericana de IA Aplicada",
    template: "%s | ALIAA",
  },
  description: SITE_DESCRIPTION,
  keywords: [
    "inteligencia artificial",
    "machine learning",
    "cursos online",
    "América Latina",
    "formación IA",
    "certificados",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" suppressHydrationWarning className={`${inter.variable} h-full`}>
      <body className="min-h-full flex flex-col antialiased">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
