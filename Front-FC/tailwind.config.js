/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bolivar: {
          50: '#E8F5E8',
          100: '#C8E6C8',
          200: '#A3D9A3',
          300: '#7ECC7E',
          400: '#5EBF5E',
          500: '#00A651', // Verde principal Bolívar
          600: '#008B43', // Verde oscuro
          700: '#007038',
          800: '#00552C',
          900: '#003A20',
        },
        gold: {
          50: '#FFFEF7',
          100: '#FFFAEB',
          200: '#FFF2CC',
          300: '#FFE999',
          400: '#FFDD66',
          500: '#FFD700', // Dorado principal
          600: '#E6C200',
          700: '#CC9900',
          800: '#B37700',
          900: '#995500',
        }
      }
    },
  },
  plugins: [],
};
