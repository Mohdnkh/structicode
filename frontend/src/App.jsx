import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppShell from './components/workspace/AppShell'
import Home from './pages/Home'
import Analyzer from './pages/Analyzer'
import StructureDesigner from './pages/StructureDesigner'

export default function App() {
  return <BrowserRouter><AppShell><Routes>
    <Route path="/" element={<Home />} />
    <Route path="/analyze" element={<Analyzer />} />
    <Route path="/structure-designer" element={<StructureDesigner />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes></AppShell></BrowserRouter>
}