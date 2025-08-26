import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  const handleLogin = async () => {
    setLoading(true)
    setMessage('')
    try {
      const res = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      const data = await res.json()

      if (res.ok && data.access_token) {
        localStorage.setItem('auth_token', data.access_token)
        navigate('/analyze')
      } else {
        setMessage(data.detail || data.message || 'Login failed.')
      }
    } catch (err) {
      console.error('Login Error:', err)
      setMessage('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundImage: 'url("/column-load-bg.png")',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '20px',
        boxShadow: '0 8px 16px rgba(0, 0, 0, 0.1)',
        maxWidth: '500px',
        width: '100%'
      }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Login</h2>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          className="input"
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          className="input"
        />

        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            marginTop: '1rem',
            width: '100%',
            padding: '12px',
            background: '#2563eb',
            color: 'white',
            fontWeight: 'bold',
            border: 'none',
            borderRadius: '10px'
          }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>

        {message && <p style={{ marginTop: '1rem', color: 'red' }}>{message}</p>}

        <p style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          Don’t have an account?{' '}
          <span
            style={{ color: '#2563eb', cursor: 'pointer', fontWeight: 'bold' }}
            onClick={() => navigate('/signup')}
          >
            Sign Up
          </span>
        </p>
      </div>
    </div>
  )
}
