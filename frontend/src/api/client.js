import { elementRequest, structureRequest } from './adapters'
import { isCapabilityResponse } from './capabilities'

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
const TOKEN_KEY = 'structicode-access-token'

export function getAccessToken() { return typeof sessionStorage === 'undefined' ? null : sessionStorage.getItem(TOKEN_KEY) }
export function setAccessToken(token) { if (typeof sessionStorage !== 'undefined') sessionStorage.setItem(TOKEN_KEY, token) }
export function clearAccessToken() {
  if (typeof sessionStorage !== 'undefined') sessionStorage.removeItem(TOKEN_KEY)
  if (typeof window !== 'undefined') window.dispatchEvent(new Event('structicode-auth-cleared'))
}
export function authHeaders(headers = {}) {
  const token = getAccessToken()
  return token ? { ...headers, Authorization: `Bearer ${token}` } : headers
}

export class ApiError extends Error {
  constructor(message, status, code, details = []) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

async function readJson(response, fallbackMessage) {
  let body
  try { body = await response.json() } catch { throw new ApiError('The API returned an unreadable response.', response.status, 'INVALID_RESPONSE') }
  if (!response.ok) {
    if (response.status === 401) clearAccessToken()
    throw new ApiError(body.error?.message || fallbackMessage, response.status, body.error?.code || 'HTTP_ERROR', body.error?.details || [])
  }
  return body
}

export async function postJson(path, payload) {
  let response
  try { response = await fetch(`${API_BASE}${path}`, { method: 'POST', headers: authHeaders({ 'Content-Type': 'application/json' }), body: JSON.stringify(payload) }) }
  catch { throw new ApiError('Could not connect to the local API.', 0, 'NETWORK_ERROR') }
  return readJson(response, 'Analysis request failed.')
}

export async function getJson(path, fallbackMessage = 'The API response was unavailable.') {
  let response
  try { response = await fetch(`${API_BASE}${path}`, { headers: authHeaders() }) } catch { throw new ApiError('Could not connect to the local API.', 0, 'NETWORK_ERROR') }
  return readJson(response, fallbackMessage)
}

export const analyzeElement = input => postJson('/api/v1/analysis/element', elementRequest(input))
export const analyzeStructure = model => postJson('/api/v1/analysis/structure', structureRequest(model))
export const getAnalysisRun = runId => getJson(`/api/v1/analysis-runs/${encodeURIComponent(runId)}`, 'Analysis run was not found.')

export async function getCapabilities() {
  const response = await getJson('/api/v1/capabilities', 'Could not load capability metadata.')
  if (!isCapabilityResponse(response)) throw new ApiError('The API returned invalid capability metadata.', 200, 'INVALID_CAPABILITIES')
  return response
}
export const getCapability = familyId => getJson(`/api/v1/capabilities/${encodeURIComponent(familyId)}`, 'Capability family was not found.')

export async function downloadTraceableReport(runId) {
  if (!runId) throw new ApiError('A server-owned analysis run is required before downloading a traceable report.', 0, 'MISSING_RUN_ID')
  let response
  try { response = await fetch(`${API_BASE}/api/v1/reports/${encodeURIComponent(runId)}.pdf`, { headers: authHeaders() }) }
  catch { throw new ApiError('Could not connect to the local API.', 0, 'NETWORK_ERROR') }
  if (!response.ok) {
    if (response.status === 401) clearAccessToken()
    let body = {}; try { body = await response.json() } catch { /* generic safe error */ }
    throw new ApiError(body.error?.message || 'Could not generate the traceable report.', response.status, body.error?.code || 'REPORT_ERROR')
  }
  return response.blob()
}

export function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.setTimeout(() => window.URL.revokeObjectURL(url), 0)
}

// Legacy compatibility only. P8 does not expose this as a primary workflow action.
export async function legacyPdf(data, result) {
  const response = await fetch(`${API_BASE}/generate-pdf`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ data, result }) })
  if (!response.ok) throw new ApiError('Could not generate the legacy PDF.', response.status, 'PDF_ERROR')
  return response.blob()
}

export const register = payload => postJson('/api/v1/auth/register', payload)
export const signIn = payload => postJson('/api/v1/auth/login', payload)
export const getCurrentUser = () => getJson('/api/v1/auth/me', 'Could not load the local user session.')
export const getOrganizations = () => getJson('/api/v1/organizations', 'Could not load local organizations.')
export const getProjects = () => getJson('/api/v1/projects', 'Could not load projects.')
export const createProject = payload => postJson('/api/v1/projects', payload)
export const getProjectRuns = projectId => getJson(`/api/v1/projects/${encodeURIComponent(projectId)}/analysis-runs`, 'Could not load project runs.')
