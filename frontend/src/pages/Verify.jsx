import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Verify() {
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  const handleVerify = async () => {
    setLoading(true)
    setMessage('')
    try {
      const res = await fetch('/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code })
      })
      const data = await res.json()

      if (res.ok) {
        setMessage(data.message)
        setTimeout(() => navigate('/login'), 1500)
      } else {
        setMessage(data.detail || 'Verification failed.')
      }
    } catch (err) {
      setMessage('Something went wrong.')
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
        <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Verify Your Email</h2>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          className="input"
        />

        <input
          type="text"
          placeholder="Verification Code"
          value={code}
          onChange={e => setCode(e.target.value)}
          className="input"
        />

        <button onClick={handleVerify} disabled={loading} style={{ marginTop: '1rem' }}>
          {loading ? 'Verifying...' : 'Verify'}
        </button>

        {message && <p style={{ marginTop: '1rem', color: '#2563eb' }}>{message}</p>}
      </div>
    </div>
  )
}
