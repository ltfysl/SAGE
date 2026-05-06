import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        dark: { 50: "#f8fafc", 900: "#0a0a0f", 950: "#050508" },
        accent: { cyan: "#22d3ee", blue: "#3b82f6", violet: "#8b5cf6", emerald: "#10b981", rose: "#f43f5e", amber: "#f59e0b" }
      },
      fontFamily: { mono: ["JetBrains Mono", "Fira Code", "monospace"] },
      animation: { "pulse-glow": "pulseGlow 2s ease-in-out infinite", "slide-up": "slideUp 0.5s ease-out" },
      keyframes: {
        pulseGlow: { "0%, 100%": { boxShadow: "0 0 20px rgba(34,211,238,0.3)" }, "50%": { boxShadow: "0 0 40px rgba(34,211,238,0.6)" } },
        slideUp: { from: { opacity: "0", transform: "translateY(20px)" }, to: { opacity: "1", transform: "translateY(0)" } }
      }
    }
  },
  plugins: []
};
export default config;
