/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        jogai: {
          bg: '#0a0e17',
          card: '#131928',
          border: '#1e293b',
          accent: '#f59e0b',
          green: '#22c55e',
          red: '#ef4444',
          text: '#e2e8f0',
          muted: '#94a3b8',
        },
      },
    },
  },
  plugins: [],
};
