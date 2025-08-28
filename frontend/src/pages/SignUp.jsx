import { useState } from "react"
import { useNavigate } from "react-router-dom"

const API_BASE = import.meta.env.VITE_API_URL || ""

export default function SignUp() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  const [step, setStep] = useState("signup") // signup | verify
  const [verifyCode, setVerifyCode] = useState("")
  const [message, setMessage] = useState({ text: "", type: "" })

  const navigate = useNavigate()

  const handleSignUp = async () => {
    if (password !== confirmPassword) {
      setMessage({ text: "❌ Passwords do not match", type: "error" })
      return
    }

    setLoading(true)
    setMessage({ text: "", type: "" })
    try {
      const res = await fetch(`${API_BASE}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })

      const data = await res.json()

      if (res.ok) {
        setStep("verify")
        setMessage({ text: "✅ Code sent to your email. Please enter it below to verify.", type: "success" })
      } else {
        setMessage({ text: data.message || data.detail || "Registration failed.", type: "error" })
      }
    } catch (err) {
      console.error("SignUp Error:", err)
      setMessage({ text: "❌ Something went wrong.", type: "error" })
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async () => {
    if (!verifyCode) {
      setMessage({ text: "❌ Please enter the verification code.", type: "error" })
      return
    }

    setLoading(true)
    setMessage({ text: "", type: "" })
    try {
      const res = await fetch(`${API_BASE}/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code: verifyCode }),
      })

      const data = await res.json()

      if (res.ok) {
        setMessage({ text: "✅ Your account has been verified. Redirecting to login...", type: "success" })
        setTimeout(() => navigate("/login"), 2000)
      } else {
        setMessage({ text: data.message || data.detail || "Verification failed.", type: "error" })
      }
    } catch (err) {
      console.error("Verify Error:", err)
      setMessage({ text: "❌ Something went wrong.", type: "error" })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f0f0f0",
        padding: "20px",
      }}
    >
      <div
        style={{
          background: "white",
          padding: "40px",
          borderRadius: "16px",
          boxShadow: "0 0 16px rgba(0,0,0,0.1)",
          width: "100%",
          maxWidth: "420px",
        }}
      >
        <h2 style={{ marginBottom: "1.5rem", fontWeight: "bold" }}>
          {step === "signup" ? "Create Account" : "Verify Your Email"}
        </h2>

        {message.text && (
          <p
            style={{
              color: message.type === "error" ? "red" : "green",
              marginBottom: "1rem",
              fontWeight: "600",
            }}
          >
            {message.text}
          </p>
        )}

        {step === "signup" && (
          <>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                width: "100%",
                padding: "10px",
                marginBottom: "1rem",
                borderRadius: "8px",
                border: "1px solid #ccc",
              }}
            />

            {/* Password */}
            <div style={{ position: "relative", marginBottom: "1rem" }}>
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{
                  width: "100%",
                  padding: "10px",
                  borderRadius: "8px",
                  border: "1px solid #ccc",
                }}
              />
              <span
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: "absolute",
                  right: "10px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  cursor: "pointer",
                }}
              >
                {showPassword ? "🙈" : "👁"}
              </span>
            </div>

            {/* Confirm Password */}
            <div style={{ position: "relative", marginBottom: "1rem" }}>
              <input
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                style={{
                  width: "100%",
                  padding: "10px",
                  borderRadius: "8px",
                  border: "1px solid #ccc",
                }}
              />
              <span
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                style={{
                  position: "absolute",
                  right: "10px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  cursor: "pointer",
                }}
              >
                {showConfirmPassword ? "🙈" : "👁"}
              </span>
            </div>

            <button
              onClick={handleSignUp}
              disabled={loading}
              style={{
                width: "100%",
                padding: "12px",
                background: "#2563eb",
                color: "white",
                fontWeight: "bold",
                border: "none",
                borderRadius: "10px",
                cursor: "pointer",
              }}
            >
              {loading ? "Registering..." : "Sign Up"}
            </button>

            <p style={{ marginTop: "1rem", textAlign: "center" }}>
              Already have an account?{" "}
              <span
                style={{ color: "#2563eb", cursor: "pointer", fontWeight: "bold" }}
                onClick={() => navigate("/login")}
              >
                Log In
              </span>
            </p>
          </>
        )}

        {step === "verify" && (
          <>
            <input
              type="text"
              placeholder="Enter verification code"
              value={verifyCode}
              onChange={(e) => setVerifyCode(e.target.value)}
              style={{
                width: "100%",
                padding: "10px",
                marginBottom: "1rem",
                borderRadius: "8px",
                border: "1px solid #ccc",
              }}
            />

            <button
              onClick={handleVerify}
              disabled={loading}
              style={{
                width: "100%",
                padding: "12px",
                background: "#16a34a",
                color: "white",
                fontWeight: "bold",
                border: "none",
                borderRadius: "10px",
                cursor: "pointer",
              }}
            >
              {loading ? "Verifying..." : "Verify Account"}
            </button>
          </>
        )}
      </div>
    </div>
  )
}
