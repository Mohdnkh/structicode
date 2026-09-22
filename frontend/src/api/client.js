import { elementRequest, structureRequest } from './adapters'

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(message, status, code, details = []) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

async function postJson(path, payload) {
  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
  } catch {
    throw new ApiError('Could not connect to the local API.', 0, 'NETWORK_ERROR')
  }
  let body
  try {
    body = await response.json()
  } catch {
    throw new ApiError('The API returned an unreadable response.', response.status, 'INVALID_RESPONSE')
  }
  if (!response.ok) {
    throw new ApiError(
      body.error?.message || 'Analysis request failed.', response.status,
      body.error?.code || 'HTTP_ERROR', body.error?.details || []
    )
  }
  return body
}

async function getJson(path) {
  let response
  try {
    response = await fetch(`${API_BASE}${path}`)
  } catch {
    throw new ApiError('Could not connect to the local API.', 0, 'NETWORK_ERROR')
  }
  let body
  try {
    body = await response.json()
  } catch {
    throw new ApiError('The API returned an unreadable response.', response.status, 'INVALID_RESPONSE')
  }
  if (!response.ok) {
    throw new ApiError(body.error?.message || 'Analysis run was not found.', response.status,
      body.error?.code || 'HTTP_ERROR', body.error?.details || [])
  }
  return body
}

export const analyzeElement = (input) =>
  postJson('/api/v1/analysis/element', elementRequest(input))

export const analyzeStructure = (model) =>
  postJson('/api/v1/analysis/structure', structureRequest(model))

export const getAnalysisRun = (runId) =>
  getJson(`/api/v1/analysis-runs/${encodeURIComponent(runId)}`)

export async function downloadTraceableReport(runId) {
  const response = await fetch(`${API_BASE}/api/v1/reports/${encodeURIComponent(runId)}.pdf`)
  if (!response.ok) {
    let body = {}
    try { body = await response.json() } catch { /* Keep a safe generic error. */ }
    throw new ApiError(body.error?.message || 'Could not generate the traceable report.', response.status,
      body.error?.code || 'REPORT_ERROR')
  }
  return response.blob()
}

// PDF remains a legacy compatibility route until P7.
export async function legacyPdf(data, result) {
  const response = await fetch(`${API_BASE}/generate-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data, result })
  })
  if (!response.ok) throw new ApiError('Could not generate the legacy PDF.', response.status, 'PDF_ERROR')
  return response.blob()
}
