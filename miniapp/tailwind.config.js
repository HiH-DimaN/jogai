/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        jogai: {
          bg: '#0f0f1a',
          card: '#1a1a2e',
          border: '#2a2a4a',
          accent: '#6c5ce7',
          green: '#00b894',
          red: '#e74c3c',
          text: '#f5f5f5',
          muted: '#8a8a9a',
        },
      },
    },
  },
  plugins: [],
};
