/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        primary: '#2563eb',
        positive: '#16a34a',
        negative: '#dc2626',
        attention: '#d97706',
      },
    },
  },
  plugins: [],
}
