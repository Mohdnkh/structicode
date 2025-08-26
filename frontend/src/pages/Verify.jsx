import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function Verify() {
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleVerify = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API_BASE}/auth/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      })

      const data = await res.json()

      if (res.ok && data.access_token) {
        // ✅ لو السيرفر برجع توكن بعد التحقق
        localStorage.setItem('auth_token', data.access_token)
        alert('✅ Verification successful! Redirecting...')
        navigate('/analyze')
      } else if (res.ok) {
        // ✅ لو السيرفر ما برجع توكن (بس بيوكد التفعيل)
        alert('✅ Verification successful! You can now log in.')
        navigate('/login')
      } else {
        setError(data.message || data.detail || 'Invalid code')
      }
    } catch (err) {
      console.error('Verify Error:', err)
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
      background: '#f9f9f9'
    }}>
      <div style={{
        background: 'white',
        padding: '40px',
        borderRadius: '16px',
        boxShadow: '0 0 16px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '400px'
      }}>
        <h2 style={{ marginBottom: '1rem', fontWeight: 'bold' }}>Verify Your Email</h2>
        <input
          type="text"
          placeholder="Enter verification code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
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
          onClick={handleVerify}
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
          {loading ? 'Verifying...' : 'Verify'}
        </button>
      </div>
    </div>
  )
}
