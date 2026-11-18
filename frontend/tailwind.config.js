/** Tokens visuais do meuSaldo (T-016).
 *
 * Direção visual: `design.md` §6.1 — fundo neutro claro, superfícies
 * brancas, uma cor principal para ações, verde para positivos, vermelho
 * para negativos e âmbar para atenção. O significado nunca deve depender
 * apenas da cor (usar rótulos/ícones/textos de apoio).
 */
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563eb',
          dark: '#1d4ed8',
          light: '#dbeafe',
        },
        positive: {
          DEFAULT: '#16a34a',
          light: '#dcfce7',
        },
        negative: {
          DEFAULT: '#dc2626',
          light: '#fee2e2',
        },
        attention: {
          DEFAULT: '#d97706',
          light: '#fef3c7',
        },
      },
      fontFamily: {
        sans: [
          'system-ui',
          '-apple-system',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
      },
      boxShadow: {
        card: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        panel: '0 4px 12px 0 rgb(0 0 0 / 0.08)',
      },
      borderRadius: {
        card: '0.5rem',
      },
    },
  },
  plugins: [],
}
