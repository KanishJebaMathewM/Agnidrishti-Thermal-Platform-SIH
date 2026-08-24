/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#F7F8F6',
        panel: '#EDEFEA',
        border: '#DFE3DC',
        ink: '#1F2A24',
        muted: '#5B6760',
        teal: { light: '#DCEEEC', mid: '#2C8C82', deep: '#155850' },
        amber: { light: '#FBEACD', mid: '#D89B2E', deep: '#8C5F14' },
        ember: { light: '#F7DCD1', mid: '#C25A34', deep: '#7A3117' },
        moss: { light: '#E4EAD4', mid: '#7A9448', deep: '#4A5C29' },
        violet: { light: '#E4E1EE', mid: '#6C63A6', deep: '#413A6B' },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '6px',
      },
    },
  },
  plugins: [],
}
