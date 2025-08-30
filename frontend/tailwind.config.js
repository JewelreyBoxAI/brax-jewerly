/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brax: {
          gold: '#D4AF37',
          darkgold: '#B8941F',
          navy: '#1B2951',
          cream: '#F8F6F0',
          slate: '#64748B'
        }
      },
      fontFamily: {
        'serif': ['Playfair Display', 'serif'],
        'sans': ['Inter', 'sans-serif']
      }
    },
  },
  plugins: [],
}