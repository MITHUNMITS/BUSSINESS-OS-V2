module.exports = {
  content: [
    "./business_os/templates/**/*.html",
    "./business_os/apps/**/templates/**/*.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "Noto Sans", "system-ui", "sans-serif"]
      }
    }
  },
  plugins: [require("@tailwindcss/forms"), require("daisyui")],
  daisyui: {
    themes: [
      {
        businessos: {
          "primary": "#1f7a68",
          "primary-content": "#ffffff",
          "secondary": "#2f4f64",
          "secondary-content": "#ffffff",
          "accent": "#b7791f",
          "accent-content": "#111827",
          "neutral": "#1f2937",
          "neutral-content": "#f9fafb",
          "base-100": "#ffffff",
          "base-200": "#f6f7f8",
          "base-300": "#e5e7eb",
          "base-content": "#111827",
          "info": "#2563eb",
          "success": "#15803d",
          "warning": "#b45309",
          "error": "#b91c1c",
          "--rounded-box": "0.5rem",
          "--rounded-btn": "0.375rem",
          "--rounded-badge": "0.375rem"
        }
      }
    ]
  }
};

