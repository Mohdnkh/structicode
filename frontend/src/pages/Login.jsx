import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [remember, setRemember] = useState(false)
  const [message, setMessage] = useState({ text: "", type: "" })
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  // ✅ إذا كان في Remember Me نخزن الإيميل ونرجعه معبّى
  useEffect(() => {
    const savedEmail = localStorage.getItem("remember_email")
    if (savedEmail) {
      setEmail(savedEmail)
      setRemember(true)
    }
  }, [])

  const handleLogin = async () => {
    setLoading(true)
    setMessage({ text: "", type: "" })

    try {
      const res = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })
      const data = await res.json()

      if (res.ok && data.access_token) {
        // ✅ نخزن التوكن
        localStorage.setItem("access_token", data.access_token)

        // ✅ Remember Me يخزن فقط الإيميل
        if (remember) {
          localStorage.setItem("remember_email", email)
        } else {
          localStorage.removeItem("remember_email")
        }

        setMessage({ text: "✅ Login successful! Redirecting...", type: "success" })
        setTimeout(() => navigate("/analyze"), 1000)
      } else {
        setMessage({ text: data.detail || data.message || "❌ Login failed.", type: "error" })
      }
    } catch (err) {
      console.error("Login Error:", err)
      setMessage({ text: "❌ Something went wrong.", type: "error" })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundImage: 'url("/column-load-bg.png")',
        backgroundSize: "cover",
        backgroundPosition: "center",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px",
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          padding: "40px",
          borderRadius: "20px",
          boxShadow: "0 8px 16px rgba(0, 0, 0, 0.1)",
          maxWidth: "480px",
          width: "100%",
        }}
      >
        <h2 style={{ fontSize: "1.75rem", fontWeight: "bold", marginBottom: "0.5rem", color: "#1e3a8a" }}>
          Welcome Back
        </h2>
        <p style={{ marginBottom: "1.5rem", color: "#4b5563" }}>
          Please log in to continue analyzing your structures.
        </p>

        {/* Email */}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="input"
          style={{ marginBottom: "1rem", width: "100%", padding: "10px" }}
        />

        {/* Password */}
        <div style={{ position: "relative", marginBottom: "1rem" }}>
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input"
            style={{ width: "100%", padding: "10px" }}
          />
          <span
            onClick={() => setShowPassword(!showPassword)}
            style={{
              position: "absolute",
              right: "10px",
              top: "50%",
              transform: "translateY(-50%)",
              cursor: "pointer",
              fontSize: "1.2rem",
            }}
          >
            {showPassword ? "🙈" : "👁"}
          </span>
        </div>

        {/* Remember Me */}
        <label style={{ display: "flex", alignItems: "center", marginBottom: "1rem", fontSize: "0.9rem" }}>
          <input
            type="checkbox"
            checked={remember}
            onChange={(e) => setRemember(e.target.checked)}
            style={{ marginRight: "8px" }}
          />
          Remember my email
        </label>

        {/* Login Button */}
        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            marginTop: "0.5rem",
            width: "100%",
            backgroundColor: "#2563eb",
            color: "white",
            padding: "12px",
            borderRadius: "10px",
            fontWeight: "600",
            border: "none",
            cursor: "pointer",
          }}
        >
          {loading ? "Logging in..." : "Login"}
        </button>

        {/* Messages */}
        {message.text && (
          <p
            style={{
              marginTop: "1rem",
              color: message.type === "error" ? "red" : "green",
              fontWeight: "600",
              textAlign: "center",
            }}
          >
            {message.text}
          </p>
        )}

        {/* Create Account */}
        <p style={{ marginTop: "1.5rem", textAlign: "center" }}>
          Don't have an account?{" "}
          <span
            style={{ color: "#2563eb", cursor: "pointer", fontWeight: "bold" }}
            onClick={() => navigate("/signup")}
          >
            Create Account
          </span>
        </p>
      </div>
    </div>
  )
}
