import type { Config } from 'tailwindcss'
import tailwindcssAnimate from 'tailwindcss-animate'

export default {
  darkMode: ['selector', '[data-theme="dark"]'],
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)',
        panel: 'var(--panel)',
        'panel-2': 'var(--panel-2)',
        border: 'var(--border)',
        text: 'var(--text)',
        'text-muted': 'var(--text-muted)',
        grid: 'var(--grid)',
        accent: 'var(--accent)',
        ok: 'var(--ok)',
        warn: 'var(--warn)',
        crit: 'var(--crit)',
        'threat-fill': 'var(--threat-fill)',
        'threat-stroke': 'var(--threat-stroke)',
        'map-bg': 'var(--map-bg)',
        mission: {
          cap: 'var(--m-cap)',
          recce: 'var(--m-recce)',
          strike: 'var(--m-strike)',
          airlift: 'var(--m-airlift)',
          tanker: 'var(--m-tanker)',
          aew: 'var(--m-aew)',
          sar: 'var(--m-sar)',
          hadr: 'var(--m-hadr)',
        },
      },
      fontFamily: {
        heading: ['Rajdhani', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [tailwindcssAnimate],
} satisfies Config
