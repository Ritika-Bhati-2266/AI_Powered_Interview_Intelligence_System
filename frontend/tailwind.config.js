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
          bg: '#05050a',         // Deep obsidian background
          dark: '#0a0a14',        // Secondary card/panel obsidian
          gray: '#141428',        // Border/input gray-blue
          light: '#1f1f3a',       // Active list item / button background
          cyan: '#00f3ff',        // Neon Cyan accent
          pink: '#ff007f',        // Neon Magenta accent
          yellow: '#ffe600',      // Warning Neon Yellow
          green: '#39ff14',       // Positive Neon Green
          purple: '#8b5cf6',      // Tech Purple
          text: '#a5a6c9',        // Slate-purple body text
          glow: 'rgba(0, 243, 255, 0.15)'
        }
      },
      fontFamily: {
        cyber: ['Orbitron', 'sans-serif'],
        tech: ['Share Tech Mono', 'monospace'],
        sans: ['Rajdhani', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'cyan-glow': '0 0 15px rgba(0, 243, 255, 0.35)',
        'pink-glow': '0 0 15px rgba(255, 0, 127, 0.35)',
        'green-glow': '0 0 15px rgba(57, 255, 20, 0.35)',
        'yellow-glow': '0 0 15px rgba(255, 230, 0, 0.35)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.5)',
      },
      backgroundImage: {
        'grid-pattern': "radial-gradient(circle, rgba(0, 243, 255, 0.08) 1px, transparent 1px)",
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'flicker': 'flicker 0.15s infinite alternate',
      },
      keyframes: {
        flicker: {
          '0%': { opacity: '0.97' },
          '100%': { opacity: '1.0' }
        }
      }
    },
  },
  plugins: [],
}
