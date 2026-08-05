/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    /*
     * WCAG 2.1 AA Responsive breakpoints:
     * - mobile: <= 767px (default, no prefix)
     * - tablet: 768px – 1199px
     * - desktop: >= 1200px
     */
    screens: {
      'mobile': '0px',
      'tablet': '768px',
      'desktop': '1200px',
    },
    extend: {
      colors: {
        "primary-fixed": "#d2e4fb",
        "surface-container-lowest": "#ffffff",
        "on-tertiary-container": "#769a7a",
        "error": "#ba1a1a",
        "on-primary-container": "#8192a7",
        "error-container": "#ffdad6",
        "on-tertiary": "#ffffff",
        "on-error": "#ffffff",
        "outline": "#74777d",
        "on-surface": "#1c1c18",
        "surface-variant": "#e5e2dc",
        "outline-variant": "#c4c6cd",
        "tertiary": "#001a07",
        "surface-container-low": "#f6f3ed",
        "surface-container": "#f0eee8",
        "tertiary-fixed": "#c6ecc8",
        "on-secondary-fixed": "#3a0b00",
        "secondary": "#9f4021",
        "tertiary-container": "#0f3018",
        "surface-dim": "#dcdad4",
        "on-tertiary-fixed": "#00210b",
        "secondary-fixed-dim": "#ffb59e",
        "on-secondary": "#ffffff",
        "on-tertiary-fixed-variant": "#2d4e33",
        "inverse-on-surface": "#f3f0ea",
        "on-primary-fixed-variant": "#38485a",
        "surface": "#fcf9f3",
        "on-error-container": "#93000a",
        "on-primary-fixed": "#0b1d2d",
        "primary-fixed-dim": "#b7c8de",
        "surface-container-high": "#ebe8e2",
        "on-surface-variant": "#44474c",
        "surface-container-highest": "#e5e2dc",
        "on-background": "#1c1c18",
        "secondary-container": "#fe8862",
        "inverse-surface": "#31312d",
        "on-secondary-container": "#732103",
        "inverse-primary": "#b7c8de",
        "surface-bright": "#fcf9f3",
        "on-secondary-fixed-variant": "#802a0b",
        "primary": "#041627",
        "surface-tint": "#4f6073",
        "background": "#fcf9f3",
        "on-primary": "#ffffff",
        "primary-container": "#1a2b3c",
        "secondary-fixed": "#ffdbd0",
        "tertiary-fixed-dim": "#aad0ad"
      },
      borderRadius: {
        "DEFAULT": "0.5rem",
        "lg": "0.75rem",
        "xl": "1rem",
        "2xl": "1.25rem",
        "full": "9999px"
      },
      /*
       * Spacing aumentado para adultos mayores.
       * touch-target-min = 3.5rem (56px) - recomendado para seniors.
       */
      spacing: {
        "stack-md": "2rem",
        "stack-sm": "1rem",
        "touch-target-min": "3.5rem",
        "gutter": "2rem",
        "base": "0.75rem",
        "margin-mobile": "1.5rem",
        "margin-desktop": "4rem",
        "stack-lg": "3.5rem"
      },
      fontFamily: {
        "lexend": ["Lexend", "sans-serif"]
      },
      /*
       * Font sizes aumentados para adultos mayores.
       * Base = 1.25rem (20px) mínimo para mejor legibilidad.
       */
      fontSize: {
        'xs': '0.875rem',
        'sm': '1rem',
        'base': '1.25rem',
        'lg': '1.375rem',
        'xl': '1.5rem',
        '2xl': '1.75rem',
        '3xl': '2.25rem',
        '4xl': '2.75rem',
        '5xl': '3.5rem',
        '6xl': '4.5rem',
      },
    },
  },
  plugins: [],
}
