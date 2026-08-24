/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#F8FAFC',
        panel: '#F1F5F9',
        border: '#E2E8F0',
        ink: '#0F172A',
        muted: '#64748B',
        teal: { light: '#E0F2F1', mid: '#0D9488', deep: '#00695C', accent: '#00897B' },
        amber: { light: '#FFEDD5', mid: '#F97316', deep: '#EA580C', text: '#C2410C' },
        ember: { light: '#FEE2E2', mid: '#EF4444', deep: '#DC2626', text: '#991B1B' },
        moss: { light: '#DCFCE7', mid: '#22C55E', deep: '#166534', text: '#15803D' },
        violet: { light: '#F3E8FF', mid: '#A855F7', deep: '#7E22CE', text: '#6B21A8' },
        blue: { light: '#E0F2FE', mid: '#0EA5E9', deep: '#0369A1', text: '#0284C7' },
        graytag: { light: '#F1F5F9', mid: '#64748B', deep: '#334155', text: '#475569' },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '8px',
        lg: '12px',
        xl: '16px',
      },
    },
  },
  plugins: [],
}
