import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "PulseOS — Real-Time Intelligence",
  description:
    "Continuously converts global, corporate, and personal signals into the highest-value action you should take right now.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
