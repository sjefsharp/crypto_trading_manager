import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Enable TypeScript support
      include: "**/*.{jsx,tsx}",
      jsxRuntime: "automatic",
    }),
  ],
  server: {
    port: 3000,
    host: "localhost",
    open: false,
    strictPort: true,
  },
  build: {
    outDir: "build",
    sourcemap: true,
    assetsDir: "static",
    // Ensure TypeScript files are handled correctly
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, "index.html"),
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@/components": path.resolve(__dirname, "./src/components"),
      "@/utils": path.resolve(__dirname, "./src/utils"),
      "@/types": path.resolve(__dirname, "./src/types"),
    },
    extensions: [".js", ".jsx", ".ts", ".tsx", ".json"],
  },
  // Explicit esbuild TypeScript configuration
  esbuild: {
    loader: "tsx",
    include: /.*\.(ts|tsx)$/,
    exclude: [],
    // Target ES2020 for better compatibility
    target: "es2020",
    jsxFactory: "React.createElement",
    jsxFragment: "React.Fragment",
  },
  // Environment variables handling
  envPrefix: "REACT_APP_",
  // Optimized dependency handling
  optimizeDeps: {
    include: ["react", "react-dom", "react-router-dom"],
  },
});
