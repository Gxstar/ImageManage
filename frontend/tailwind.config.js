/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{vue,js,ts,jsx,tsx,html,scss}'],
  theme: {
    extend: {
      colors: {
        primary: '#60a5fa', // light blue-400
        secondary: '#38bdf8', // light blue-300
        accent: '#0ea5e9', // light blue-500
        neutral: '#0369a1' // light blue-700
      },
      borderRadius: {
        'none': '0px',
        'sm': '2px',
        DEFAULT: '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '20px',
        '3xl': '24px',
        'full': '9999px',
        'button': '4px'
      }
    },
  },
  plugins: [],
}

