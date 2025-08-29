import React from "react"
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom"
import Home from "./pages/Home"
import Analyzer from "./pages/Analyzer"
import StructureDesigner from "./pages/StructureDesigner"   // ✅ جديد

// ✅ صفحة البداية
function HomeWrapper() {
  const navigate = useNavigate()
  const goStart = () => {
    // دايمًا يروح مباشرة على صفحة التحليل
    navigate("/analyze")
  }

  return <Home onStart={goStart} />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomeWrapper />} />

        <Route path="/analyze" element={<Analyzer />} />

        {/* ✅ الراوت الجديد لواجهة تحليل الهيكل */}
        <Route path="/structure-designer" element={<StructureDesigner />} />

        {/* أي رابط غلط يرجع للصفحة الرئيسية */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
