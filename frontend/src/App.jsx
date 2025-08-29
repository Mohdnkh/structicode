import React from "react"
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom"
import Home from "./pages/Home"
import Analyzer from "./pages/Analyzer"
import StructureDesigner from "./pages/StructureDesigner"   // ✅ جديد





// ✅ صفحة البداية
function HomeWrapper() {
  const navigate = useNavigate()
  const goStart = () => {
  
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
    </BrowserRouter>
  )
}
