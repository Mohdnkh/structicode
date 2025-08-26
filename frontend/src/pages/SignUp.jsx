import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function SignUp() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  const handleSignUp = async () => {
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const data = await res.json()

      if (res.ok) {
        alert('✅ Code sent to your email. Please verify your account.')
        navigate('/verify')
      } else {
        setError(data.message || data.detail || 'Registration failed. Please try again.')
      }
    } catch (err) {
      console.error('SignUp Error:', err)
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#f0f0f0'
    }}>
      <div style={{
        background: 'white',
        padding: '40px',
        borderRadius: '16px',
        boxShadow: '0 0 16px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '420px'
      }}>
        <h2 style={{ marginBottom: '1.5rem', fontWeight: 'bold' }}>Create Account</h2>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{
            width: '100%',
            padding: '10px',
            marginBottom: '1rem',
            borderRadius: '8px',
            border: '1px solid #ccc'
          }}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{
            width: '100%',
            padding: '10px',
            marginBottom: '1rem',
            borderRadius: '8px',
            border: '1px solid #ccc'
          }}
        />

        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          style={{
            width: '100%',
            padding: '10px',
            marginBottom: '1rem',
            borderRadius: '8px',
            border: '1px solid #ccc'
          }}
        />

        {error && <p style={{ color: 'red', marginBottom: '1rem' }}>{error}</p>}

        <button
          onClick={handleSignUp}
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            background: '#2563eb',
            color: 'white',
            fontWeight: 'bold',
            border: 'none',
            borderRadius: '10px',
            cursor: 'pointer'
          }}
        >
          {loading ? 'Registering...' : 'Sign Up'}
        </button>

        <p style={{ marginTop: '1rem', textAlign: 'center' }}>
          Already have an account?{' '}
          <span
            style={{ color: '#2563eb', cursor: 'pointer', fontWeight: 'bold' }}
            onClick={() => navigate('/login')}
          >
            Log In
          </span>
        </p>
      </div>
    </div>
  )
}
