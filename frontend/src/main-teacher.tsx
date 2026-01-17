/**
 * Teacher Dashboard Main Entry (Port 2000)
 * ISAVS 2026 Dual Portal Architecture
 */
import React from 'react'
import ReactDOM from 'react-dom/client'
import TeacherDashboard from './pages/TeacherDashboard.jsx'
import './index.css'

console.log('🎓 ISAVS Teacher Dashboard Starting...')
console.log('📍 Port: 2001')
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
    console.error('❌ Teacher Dashboard Error:', error, errorInfo)
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
            <h1 style={{ fontSize: '24px', marginBottom: '10px' }}>⚠️ Teacher Dashboard Error</h1>
            <p style={{ color: '#a1a1aa', marginBottom: '20px' }}>
              {this.state.error?.message || 'Unknown error'}
            </p>
            <button 
              onClick={() => window.location.reload()}
              style={{
                padding: '12px 24px',
                background: 'linear-gradient(135deg, #3B82F6 0%, #A78BFA 100%)',
                border: 'none',
                borderRadius: '8px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              Reload Dashboard
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
        <TeacherDashboard />
      </ErrorBoundary>
    </React.StrictMode>,
  )
  console.log('✅ Teacher Dashboard Mounted')
} catch (error) {
  console.error('❌ Fatal error:', error)
}
