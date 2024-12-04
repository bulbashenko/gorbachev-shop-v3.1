import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      keyframes: {
        pulsate: {
          '0%, 100%': { filter: 'brightness(100%)' },
          '50%': { filter: 'brightness(110%)' },
        },
      },
      animation: {
        'pulsate-slow': 'pulsate 5s infinite',
      },
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        "secondary": "var(--secondary)",
      },
    },
  },
  darkMode: "class",
  plugins: [
    require('tailwindcss-animate')
  ],
} satisfies Config;
