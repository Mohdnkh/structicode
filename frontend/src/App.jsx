import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Analyzer from './pages/Analyzer'
import Register from './pages/Register'
import Verify from './pages/Verify'
import Login from './pages/Login'





export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/register" element={<Register />} />
      <Route path="/verify" element={<Verify />} />
      <Route path="/login" element={<Login />} />
      <Route path="/analyze" element={<Analyzer />} />
    </Routes>
  )
}
