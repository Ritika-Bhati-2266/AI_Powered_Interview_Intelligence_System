/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          950: "#030712", // obsidian background
          900: "#0b0f19", // deep dashboard card
          800: "#111827", // solid slate dark
          700: "#1f2937",
          glow: {
            purple: "#a855f7",
            cyan: "#06b6d4",
            pink: "#ec4899"
          }
        }
      },
      fontFamily: {
        sans: ["Outfit", "Inter", "sans-serif"],
      },
      backgroundImage: {
        "neon-gradient": "linear-gradient(to right, #6366f1, #a855f7, #ec4899)",
        "neon-radial": "radial-gradient(circle, rgba(168,85,247,0.15) 0%, rgba(3,7,18,0) 70%)"
      },
      boxShadow: {
        "neon-cyan": "0 0 15px rgba(6, 182, 212, 0.4)",
        "neon-purple": "0 0 15px rgba(168, 85, 247, 0.4)",
        "neon-card": "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
      }
    },
  },
  plugins: [],
}
