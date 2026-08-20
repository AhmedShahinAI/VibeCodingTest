/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  // Logical properties (ms-*, me-*, ps-*, pe-*, text-start, text-end) are
  // native to Tailwind 3.3+ and flip automatically with the `dir` attribute,
  // so RTL/LTR (constitution Principle III) needs no separate plugin/theme —
  // just consistent use of logical over physical (left/right) utilities.
  plugins: [],
};
