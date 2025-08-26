import React from "react"
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom"
import Home from "./pages/Home"
import Analyzer from "./pages/Analyzer"
import SignUp from "./pages/SignUp"
import Verify from "./pages/Verify"
import Login from "./pages/Login"

// ✅ فحص اذا المستخدم مسجل دخول (باستخدام access_token)
const isAuthed = () => Boolean(localStorage.getItem("access_token"))

// ✅ مكون لحماية الصفحات (ما يفتحها غير المسجلين)
function PrivateRoute({ children }) {
  return isAuthed() ? children : <Navigate to="/login" replace />
}

// ✅ مكون يمنع الدخول لصفحات login/signup/verify اذا الشخص مسجل أصلاً
function UnauthOnly({ children }) {
  return isAuthed() ? <Navigate to="/analyze" replace /> : children
}

// ✅ صفحة البداية
function HomeWrapper() {
  const navigate = useNavigate()
  const goStart = () => {
    if (isAuthed()) {
      navigate("/analyze")
    } else {
      navigate("/login")
    }
  }

  return <Home onStart={goStart} />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomeWrapper />} />

        <Route
          path="/login"
          element={
            <UnauthOnly>
              <Login />
            </UnauthOnly>
          }
        />

        <Route
          path="/signup"
          element={
            <UnauthOnly>
              <SignUp />
            </UnauthOnly>
          }
        />

        <Route
          path="/verify"
          element={
            <UnauthOnly>
              <Verify />
            </UnauthOnly>
          }
        />

        <Route
          path="/analyze"
          element={
            <PrivateRoute>
              <Analyzer />
            </PrivateRoute>
          }
        />

        {/* أي رابط غلط يرجع للصفحة الرئيسية */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
