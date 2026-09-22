export const ACTIVE_PROJECT_KEY = 'structicode-active-project'

export function getActiveProjectId() {
  return typeof sessionStorage === 'undefined' ? null : sessionStorage.getItem(ACTIVE_PROJECT_KEY)
}

export function setActiveProjectId(projectId) {
  if (typeof sessionStorage === 'undefined') return
  if (projectId) sessionStorage.setItem(ACTIVE_PROJECT_KEY, projectId)
  else sessionStorage.removeItem(ACTIVE_PROJECT_KEY)
}

export function projectAnalysisContext(isAuthenticated, projectId) {
  return isAuthenticated && projectId ? { projectId } : {}
}
