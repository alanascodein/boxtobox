import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f2fbf4",
          100: "#e0f7e3",
          200: "#c2edc9",
          300: "#95dc9f",
          400: "#62c46f",
          500: "#3da94c",
          600: "#2b883a",
          700: "#246b31",
          800: "#20552b",
          900: "#1c4626",
          950: "#0c2714",
        },
        cream: "#faf9f4",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        display: ["Sora", "Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(16,44,22,.06), 0 4px 16px rgba(16,44,22,.08)",
        lift: "0 4px 8px rgba(16,44,22,.08), 0 12px 32px rgba(16,44,22,.14)",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: ".55" },
        },
      },
      animation: {
        fadeUp: "fadeUp .45s ease both",
        pulseSoft: "pulseSoft 1.6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
export default config;
