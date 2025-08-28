import React from "react"
import { Routes, Route, Navigate, useNavigate } from "react-router-dom"
import Home from "./pages/Home"
import Analyzer from "./pages/Analyzer"
import SignUp from "./pages/SignUp"
import Login from "./pages/Login"
import StructureDesigner from "./pages/StructureDesigner"   // ✅ جديد

// ✅ فحص اذا المستخدم مسجل دخول (باستخدام access_token)
const isAuthed = () => Boolean(localStorage.getItem("access_token"))

// ✅ مكون لحماية الصفحات (ما يفتحها غير المسجلين)
function PrivateRoute({ children }) {
  return isAuthed() ? children : <Navigate to="/login" replace />
}

// ✅ مكون يمنع الدخول لصفحات login/signup اذا الشخص مسجل أصلاً
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
        path="/analyze"
        element={
          <PrivateRoute>
            <Analyzer />
          </PrivateRoute>
        }
      />

      {/* ✅ الراوت الجديد لواجهة تحليل الهيكل */}
      <Route
        path="/structure-designer"
        element={
          <PrivateRoute>
            <StructureDesigner />
          </PrivateRoute>
        }
      />

      {/* أي رابط غلط يرجع للصفحة الرئيسية */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
