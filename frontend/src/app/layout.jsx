import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({ subsets: ["latin"] });

export const metadata = {
  title: "NeoBank | Digital Account Opening",
  description: "Open your digital bank account in minutes.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={outfit.className}>{children}</body>
    </html>
  );
}
          //  const verificationLink = `${process.env.NEXT_PUBLIC_BASE_URL}/verify?token=${token}`;   