/**
 * Student Kiosk Main Entry (Port 2001)
 * ISAVS 2026 Dual Portal Architecture
 */
import React from 'react'
import ReactDOM from 'react-dom/client'
import StudentPortal from './pages/StudentPortal.jsx'
import './index.css'

console.log('🎒 ISAVS Student Kiosk Starting...')
console.log('📍 Port: 2002')
console.log('🔧 Backend: http://localhost:6000')

// Enhanced Error Boundary
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: any }
> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: any) {
    return { hasError: true, error }
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error('❌ Student Kiosk Error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          minHeight: '100vh', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          background: '#0f0d1a',
          color: 'white',
          padding: '20px',
          textAlign: 'center'
        }}>
          <div>
            <h1 style={{ fontSize: '24px', marginBottom: '10px' }}>⚠️ Student Kiosk Error</h1>
            <p style={{ color: '#a1a1aa', marginBottom: '20px' }}>
              {this.state.error?.message || 'Unknown error'}
            </p>
            <button 
              onClick={() => window.location.reload()}
              style={{
                padding: '12px 24px',
                background: 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
                border: 'none',
                borderRadius: '8px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              Reload Kiosk
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

try {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <ErrorBoundary>
        <StudentPortal />
      </ErrorBoundary>
    </React.StrictMode>,
  )
  console.log('✅ Student Kiosk Mounted')
} catch (error) {
  console.error('❌ Fatal error:', error)
}
