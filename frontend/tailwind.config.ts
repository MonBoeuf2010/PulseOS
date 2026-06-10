import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#07090d",
          900: "#0b0e14",
          850: "#10141c",
          800: "#161b26",
          700: "#1f2633",
          600: "#2b3445",
        },
        accent: {
          DEFAULT: "#5b8cff",
          soft: "#7aa2ff",
          glow: "#3b6cff",
        },
        signal: {
          green: "#2fd27a",
          amber: "#f2b53b",
          red: "#f25f5f",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        card: "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 8px 30px -12px rgba(0,0,0,0.6)",
        glow: "0 0 0 1px rgba(91,140,255,0.35), 0 8px 40px -10px rgba(59,108,255,0.45)",
      },
    },
  },
  plugins: [],
};

export default config;
