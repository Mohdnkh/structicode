import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Analyzer from './pages/Analyzer'

export default function App() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', color: '#1f2937' }}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/analyze" element={<Analyzer />} />
      </Routes>
    </div>
  )
}
