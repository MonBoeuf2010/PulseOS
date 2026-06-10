import type { Config } from "tailwindcss";

// Tokens mirror the Webflow-inspired DESIGN.md at the repo root.
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#ffffff",
        "canvas-soft": "#fafafa",
        primary: "#080808",
        "on-primary": "#ffffff",
        ink: "#080808",
        "ink-strong": "#222222",
        body: "#363636",
        "body-mid": "#5a5a5a",
        mute: "#898989",
        "mute-soft": "#ababab",
        hairline: "#d8d8d8",
        "hairline-soft": "#ececec",
        accent: {
          purple: "#7a3dff",
          pink: "#ed52cb",
          blue: "#3b89ff",
          "blue-deep": "#006acc",
          "blue-info": "#146ef5",
          orange: "#ff6b00",
          green: "#00d722",
          yellow: "#ffae13",
          red: "#ee1d36",
        },
        // Confidence / status — slightly deepened for legibility on a white canvas.
        signal: {
          green: "#0a9a28",
          amber: "#b97e00",
          red: "#d11f33",
        },
      },
      borderRadius: {
        none: "0px",
        xs: "2px",
        sm: "4px",
        md: "8px",
        lg: "12px",
        full: "9999px",
      },
      spacing: {
        xxs: "2px",
        xs: "4px",
        sm: "8px",
        md: "12px",
        lg: "16px",
        xl: "20px",
        "2xl": "24px",
        "3xl": "32px",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["Inconsolata", "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      letterSpacing: {
        tightest: "-0.8px",
        eyebrow: "1.5px",
      },
      boxShadow: {
        // Level 1 hairline is handled by borders; these are the layered drop recipes.
        card: "0 1px 2px rgba(0,0,0,0.04), 0 10px 24px -16px rgba(0,0,0,0.12)",
        lift: "0 84px 24px rgba(0,0,0,0), 0 54px 22px rgba(0,0,0,0.01), 0 30px 18px rgba(0,0,0,0.04), 0 13px 13px rgba(0,0,0,0.08), 0 3px 7px rgba(0,0,0,0.09)",
        "lift-strong":
          "0 30px 18px rgba(0,0,0,0.05), 0 13px 13px rgba(0,0,0,0.09), 0 3px 7px rgba(0,0,0,0.12)",
        modal: "0 24px 24px rgba(0,0,0,0.26), 0 6px 13px rgba(0,0,0,0.29)",
      },
    },
  },
  plugins: [],
};

export default config;
