import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Load env file based on mode
  const env = loadEnv(mode, process.cwd(), '')
  
  // Determine configuration based on mode
  const isTeacher = mode === 'teacher'
  const isStudent = mode === 'student'
  
  // ISAVS 2026 Dual Portal Architecture
  // Port 2001: Teacher Dashboard (Session Management, Real-time Monitoring)
  // Port 2002: Student Kiosk (GPS Check, OTP Entry, Face Verification)
  let port = 5173 // Default unified app
  let htmlInput = './index.html'
  
  if (isTeacher) {
    port = 2001
    htmlInput = './teacher.html'
  } else if (isStudent) {
    port = 2002
    htmlInput = './student.html'
  }
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    build: {
      outDir: isTeacher ? 'dist-teacher' : isStudent ? 'dist-student' : 'dist',
      sourcemap: false,
      rollupOptions: {
        input: htmlInput,
      },
    },
    server: {
      port,
      host: true, // Expose to network for mobile access
      proxy: {
        '/api': {
          target: 'http://localhost:6000',
          changeOrigin: true,
        },
        '/ws': {
          target: 'ws://localhost:6000',
          ws: true,
        },
      },
    },
  }
})
