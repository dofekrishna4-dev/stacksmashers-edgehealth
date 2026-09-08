/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: {
          950: "#05070d",
          900: "#0a0e18",
          850: "#0d1220",
          800: "#121a2b",
          700: "#1a2338",
        },
        line: "rgba(255,255,255,0.08)",
        cyan: {
          accent: "#3fd8e0",
        },
        teal: {
          accent: "#34d399",
        },
        violet: {
          accent: "#a78bfa",
        },
        ink: {
          primary: "#eef1fa",
          secondary: "#96a0c0",
          muted: "#5d6690",
        },
      },
      fontFamily: {
        sans: ["Space Grotesk", "Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        panel: "14px",
      },
    },
  },
  plugins: [],
}