import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

import { elementRequest, structureRequest } from '../src/api/adapters.js'
import { projectAnalysisContext } from '../src/context/projectState.js'

test('project identifiers enter only selected project analysis envelopes', () => {
  const beam = { type: 'Normal', width: 30, depth: 60, length: 5, cover: 3, fc: 25, fy: 420, rebar: { count: 4, diameter: 16 }, loads: { dead: 5, live: 0, wind: 0, snow: 0, earthquake: 0 } }
  assert.equal(elementRequest({ code: 'aci', element: 'beam', formData: beam }).project_id, undefined)
  assert.equal(elementRequest({ code: 'aci', element: 'beam', formData: beam, projectId: 'project-1' }).project_id, 'project-1')
  const model = { code: 'aci', projectId: 'project-2', materials: [], sections: [], nodes: [], members: [], slabs: [] }
  assert.equal(structureRequest(model).project_id, 'project-2')
  assert.deepEqual(projectAnalysisContext(false, 'project-1'), {})
  assert.deepEqual(projectAnalysisContext(true, null), {})
  assert.deepEqual(projectAnalysisContext(true, 'project-1'), { projectId: 'project-1' })
})

test('identity client centralizes bearer injection and clears a rejected session', async () => {
  const [source, projectContext] = await Promise.all([
    readFile(new URL('../src/api/client.js', import.meta.url), 'utf8'),
    readFile(new URL('../src/context/ProjectContext.jsx', import.meta.url), 'utf8'),
  ])
  assert.match(source, /function authHeaders/)
  assert.match(source, /Authorization: `Bearer \$\{token\}`/)
  assert.match(source, /response\.status === 401\) clearAccessToken/)
  assert.match(source, /sessionStorage/)
  assert.match(projectContext, /structicode-auth-cleared/)
  assert.match(projectContext, /setActiveProjectId\(null\)/)
})

test('stale projects are replaced and report 401 clears the same session', async () => {
  const [projects, client] = await Promise.all([
    readFile(new URL('../src/pages/Projects.jsx', import.meta.url), 'utf8'),
    readFile(new URL('../src/api/client.js', import.meta.url), 'utf8'),
  ])
  assert.match(projects, /activeProjectId !== selected\.id/)
  assert.match(projects, /reason\.status === 404/)
  assert.match(client, /downloadTraceableReport[\s\S]*response\.status === 401[\s\S]*clearAccessToken/)
  assert.deepEqual(projectAnalysisContext(false, 'user-a-project'), {})
  assert.deepEqual(projectAnalysisContext(true, 'user-b-project'), { projectId: 'user-b-project' })
})

test('persistence notices distinguish local project records from ephemeral records', async () => {
  const [report, analyzer, structure, english, arabic] = await Promise.all([
    readFile(new URL('../src/components/workspace/ReportAction.jsx', import.meta.url), 'utf8'),
    readFile(new URL('../src/pages/Analyzer.jsx', import.meta.url), 'utf8'),
    readFile(new URL('../src/pages/StructureDesigner.jsx', import.meta.url), 'utf8'),
    readFile(new URL('../src/locales/en/translation.json', import.meta.url), 'utf8').then(JSON.parse),
    readFile(new URL('../src/locales/ar/translation.json', import.meta.url), 'utf8').then(JSON.parse),
  ])
  assert.match(report, /PROJECT_PERSISTED/)
  assert.match(analyzer, /projectAnalysisContext/)
  assert.match(structure, /projectAnalysisContext/)
  for (const key of ['identity.sign_in', 'projects.title', 'projects.persisted_detail', 'projects.ephemeral_detail', 'report.persisted']) { assert.ok(english[key]); assert.ok(arabic[key]) }
})
