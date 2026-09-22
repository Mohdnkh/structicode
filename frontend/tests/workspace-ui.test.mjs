import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import {
  capabilityWarning, elementCapability, isElementSelectable, isStructureSelectable,
  sourceBlockedTargets,
} from '../src/api/capabilities.js'

const legacy = { status: 'LEGACY_UNVERIFIED', v1_route: true, legacy_route: true, note: 'Legacy route.' }
const unavailable = { status: 'NOT_IMPLEMENTED', v1_route: false, legacy_route: false, note: 'Unavailable.' }
const family = (id, elements, structure = legacy, targets = []) => ({ family_id: id, element_capabilities: elements, structure_analysis: structure, verification_targets: targets })
const allElements = values => Object.entries(values).map(([element_id, capability]) => ({ element_id, capability }))

test('capability helpers preserve backend route truth', () => {
  const steel = family('steel', allElements({ beam: unavailable, column: unavailable, slab: unavailable, footing: unavailable, staircase: unavailable, steel_beam: legacy, steel_column: legacy }), unavailable, [{ target_id: 'aisc_360_22', status: 'SOURCE_BLOCKED' }])
  const indian = family('is', allElements({ beam: legacy, steel_beam: unavailable, steel_column: unavailable }), legacy)
  assert.equal(isElementSelectable(steel, 'beam'), false)
  assert.equal(isElementSelectable(steel, 'steel_beam'), true)
  assert.equal(isElementSelectable(steel, 'steel_column'), true)
  assert.equal(isElementSelectable(indian, 'steel_beam'), false)
  assert.equal(isStructureSelectable(steel), false)
  assert.equal(elementCapability(steel, 'steel_beam').status, 'LEGACY_UNVERIFIED')
  assert.equal(sourceBlockedTargets(steel)[0].target_id, 'aisc_360_22')
  assert.match(capabilityWarning(legacy), /unverified/i)
  assert.match(capabilityWarning(unavailable), /not implemented/i)
})

test('source-blocked targets are never represented as current verification', () => {
  const target = { target_id: 'aci_318_25', status: 'SOURCE_BLOCKED' }
  assert.equal(sourceBlockedTargets(family('aci', [], legacy, [target]))[0].status, 'SOURCE_BLOCKED')
  assert.doesNotMatch(capabilityWarning({ status: 'SOURCE_BLOCKED' }), /verified/i)
})

test('primary P8 report paths require a server-owned run ID and avoid legacy PDF generation', async () => {
  const [analyzer, structure, reportAction] = await Promise.all([
    readFile(new URL('../src/pages/Analyzer.jsx', import.meta.url), 'utf8'),
    readFile(new URL('../src/pages/StructureDesigner.jsx', import.meta.url), 'utf8'),
    readFile(new URL('../src/components/workspace/ReportAction.jsx', import.meta.url), 'utf8'),
  ])
  assert.match(analyzer, /downloadTraceableReport/)
  assert.match(structure, /downloadTraceableReport/)
  assert.doesNotMatch(analyzer, /legacyPdf/)
  assert.doesNotMatch(structure, /legacyPdf/)
  assert.match(reportAction, /typeof runId === 'string'/)
})

test('home source does not retain unsupported universal compliance claims', async () => {
  const [home, english, arabic] = await Promise.all([
    readFile(new URL('../src/pages/Home.jsx', import.meta.url), 'utf8'),
    readFile(new URL('../src/locales/en/translation.json', import.meta.url), 'utf8'),
    readFile(new URL('../src/locales/ar/translation.json', import.meta.url), 'utf8'),
  ])
  const text = `${home}\n${english}\n${arabic}`
  assert.doesNotMatch(text, /Code-compliant design and analysis for all structural elements/i)
  assert.doesNotMatch(text, /جميع الأكواد العالمية/)
  assert.match(text, /explicit capability and verification status/i)
})