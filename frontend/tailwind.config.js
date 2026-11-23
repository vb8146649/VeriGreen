module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./index.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0fdf4",
          100: "#dcfce7",
          500: "#22c55e",
          700: "#15803d",
          900: "#14532d",
        },
        accent: "#D97706",
        dark: "#13261B",
      },
    },
  },
  plugins: [],
};
