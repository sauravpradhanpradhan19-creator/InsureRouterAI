import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:     { primary: '#0A0A0F', secondary: '#111118', tertiary: '#1A1A24' },
        accent: { primary: '#6366F1', glow: '#818CF8', success: '#10B981', warning: '#F59E0B', danger: '#EF4444' },
        border: { DEFAULT: '#1E1E2E', accent: '#6366F1' },
        text:   { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#475569' },
      },
    },
  },
  plugins: [],
}
export default config
