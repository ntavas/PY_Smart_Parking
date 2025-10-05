import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,        // 0.0.0.0
    port: 5173,        // fixed
    strictPort: true,  // fail if taken instead of switching ports
    hmr: { clientPort: 443 } // important for VS Code public HTTPS tunnel
  }
})
