import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppShell from './components/workspace/AppShell'
import Home from './pages/Home'
import Analyzer from './pages/Analyzer'
import StructureDesigner from './pages/StructureDesigner'
import SignIn from './pages/SignIn'
import Projects from './pages/Projects'
import { AuthProvider } from './context/AuthContext'
import { ProjectProvider } from './context/ProjectContext'

export default function App() {
  return <BrowserRouter><AuthProvider><ProjectProvider><AppShell><Routes>
    <Route path="/" element={<Home />} />
    <Route path="/analyze" element={<Analyzer />} />
    <Route path="/structure-designer" element={<StructureDesigner />} />
    <Route path="/sign-in" element={<SignIn />} />
    <Route path="/projects" element={<Projects />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes></AppShell></ProjectProvider></AuthProvider></BrowserRouter>
}
