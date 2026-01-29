import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    force: true
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    watch: {
      usePolling: true,
      interval: 300,
      // ignored: ["**/.env", "**/.env.*"]
    },
    hmr: {
      overlay: true
    },
  }
});
