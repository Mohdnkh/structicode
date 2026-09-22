import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { getActiveProjectId, setActiveProjectId } from './projectState'

const ProjectContext = createContext(null)
export function ProjectProvider({ children }) {
  const [activeProjectId, setState] = useState(getActiveProjectId)
  useEffect(() => {
    const clearProject = () => { setActiveProjectId(null); setState(null) }
    window.addEventListener('structicode-auth-cleared', clearProject)
    return () => window.removeEventListener('structicode-auth-cleared', clearProject)
  }, [])
  const value = useMemo(() => ({ activeProjectId, selectProject(projectId) { setActiveProjectId(projectId); setState(projectId || null) } }), [activeProjectId])
  return <ProjectContext.Provider value={value}>{children}</ProjectContext.Provider>
}
export function useProject() { const context = useContext(ProjectContext); if (!context) throw new Error('ProjectProvider is required'); return context }
