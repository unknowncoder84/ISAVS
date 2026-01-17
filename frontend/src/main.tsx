import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

console.log('🚀 ISAVS 2026 Starting...')
console.log('📍 Backend API:', import.meta.env.VITE_API_URL || 'http://localhost:6000')

// Enhanced Error Boundary with detailed logging
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: any; errorInfo: any }
> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error: any) {
    console.error('🔴 Error Boundary Caught:', error)
    return { hasError: true, error }
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error('❌ React Error Details:', {
      error: error.toString(),
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString()
    })
    this.setState({ errorInfo })
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
          <div style={{ maxWidth: '600px' }}>
            <div style={{
              width: '80px',
              height: '80px',
              margin: '0 auto 20px',
              background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '40px'
            }}>
              ⚠️
            </div>
            <h1 style={{ fontSize: '28px', marginBottom: '10px', fontWeight: 'bold' }}>
              System Error
            </h1>
            <p style={{ color: '#a1a1aa', marginBottom: '20px', fontSize: '16px' }}>
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            {this.state.errorInfo && (
              <details style={{ 
                marginBottom: '20px', 
                textAlign: 'left', 
                background: 'rgba(255,255,255,0.05)',
                padding: '15px',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#71717a'
              }}>
                <summary style={{ cursor: 'pointer', marginBottom: '10px', color: '#a1a1aa' }}>
                  Technical Details
                </summary>
                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
            <button 
              onClick={() => window.location.reload()}
              style={{
                padding: '14px 32px',
                background: 'linear-gradient(135deg, #3B82F6 0%, #A78BFA 100%)',
                border: 'none',
                borderRadius: '12px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: '600',
                boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)'
              }}
            >
              🔄 Reload Application
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Initialize application with comprehensive error handling
try {
  const rootElement = document.getElementById('root')
  
  if (!rootElement) {
    throw new Error('Root element not found. DOM may not be ready.')
  }

  console.log('✅ Root element found')
  console.log('🎨 Initializing React...')

  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </React.StrictMode>,
  )
  
  console.log('✅ ISAVS 2026 Mounted Successfully')
  console.log('🌐 Frontend: http://localhost:2000')
  console.log('🔧 Backend: http://localhost:6000')
  
} catch (error) {
  console.error('❌ Fatal Initialization Error:', error)
  
  // Fallback UI for catastrophic failures
  document.body.innerHTML = `
    <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #0f0d1a; color: white; padding: 20px; text-align: center; font-family: system-ui, -apple-system, sans-serif;">
      <div style="max-width: 500px;">
        <div style="width: 80px; height: 80px; margin: 0 auto 20px; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 40px;">
          ⚠️
        </div>
        <h1 style="font-size: 28px; margin-bottom: 10px; font-weight: bold;">Failed to Start</h1>
        <p style="color: #a1a1aa; margin-bottom: 20px; font-size: 16px;">
          ISAVS could not initialize. Please check the console for details.
        </p>
        <button 
          onclick="window.location.reload()"
          style="padding: 14px 32px; background: linear-gradient(135deg, #3B82F6 0%, #A78BFA 100%); border: none; border-radius: 12px; color: white; cursor: pointer; font-size: 16px; font-weight: 600; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);"
        >
          🔄 Reload Page
        </button>
      </div>
    </div>
  `
}
