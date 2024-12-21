/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4169E1',
        secondary: '#6B7280',
        background: '#F5F5F5',
        surface: '#FFFFFF',
      },
      spacing: {
        'sidebar': '72px',
        'sidebar-expanded': '250px',
      },
    },
  },
  plugins: [],
}
