import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  server: { port: 5188, host: true },
  build: { target: "es2022", chunkSizeWarningLimit: 900 },
  test: { environment: "node", include: ["tests/**/*.test.ts"] },
} as any);
