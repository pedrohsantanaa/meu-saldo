/** Tokens visuais do Cifaro, alinhados ao protótipo aprovado
 * (`docs/interface.png`).
 *
 * - Sidebar azul-marinho escuro com item ativo azul.
 * - Verde é a cor das ações primárias ("+ Nova Movimentação").
 * - Roxo para investimentos, laranja para despesas variáveis,
 *   vermelho para despesas, azul para despesas fixas.
 * - O significado nunca deve depender apenas da cor (usar rótulos/
 *   ícones/textos de apoio).
 */
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        sidebar: {
          DEFAULT: '#1e2a44',
          hover: '#2a3a5c',
          text: '#cbd5e1',
        },
        primary: {
          DEFAULT: '#2563eb',
          dark: '#1d4ed8',
          light: '#dbeafe',
        },
        action: {
          DEFAULT: '#16a34a',
          dark: '#15803d',
          light: '#dcfce7',
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
        variable: {
          DEFAULT: '#f97316',
          light: '#ffedd5',
        },
        investment: {
          DEFAULT: '#8b5cf6',
          light: '#ede9fe',
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
