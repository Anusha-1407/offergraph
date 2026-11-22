/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#060913',
          900: '#0b1120',
          850: '#0f172a',
          800: '#142036',
          700: '#1e293b',
          600: '#334155',
        },
        cyber: {
          blue: '#38bdf8',
          cyan: '#06b6d4',
          purple: '#818cf8',
          violet: '#a855f7',
          red: '#ef4444',
          amber: '#f59e0b',
          green: '#10b981',
          emerald: '#059669',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Consolas', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
