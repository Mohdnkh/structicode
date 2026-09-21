import assert from 'node:assert/strict'
import test from 'node:test'

import { elementRequest, structureRequest } from '../src/api/adapters.js'

test('beam form values retain display units with explicit v1 field suffixes', () => {
  const formData = {
    type: 'Normal', width: 30, depth: 60, length: 5, cover: 3,
    fc: 25, fy: 420, rebar: { count: 4, diameter: 16 },
    loads: { dead: 5, live: 3, wind: 0, snow: 0 }
  }
  const original = structuredClone(formData)
  const request = elementRequest({ code: 'ACI', element: 'beam', formData })
  assert.equal(request.code_id, 'aci')
  assert.equal(request.input.width_cm, 30)
  assert.equal(request.input.span_m, 5)
  assert.equal(request.input.line_loads_kn_per_m.dead, 5)
  assert.deepEqual(formData, original)
})

test('steel beam span is sent as millimetres, without reinterpretation', () => {
  const request = elementRequest({
    code: 'ACI', element: 'steel_beam',
    formData: {
      sectionType: 'IPE', sectionSize: 'IPE100',
      dimensions: { depth: 100, width: 55, flangeThickness: 7.1, webThickness: 4.1 },
      steelGrade: 235, span: 5000, uniformLoad: 5,
      supportType: 'Simply Supported'
    }
  })
  assert.equal(request.input.span_mm, 5000)
  assert.equal(request.input.support_type, 'simply_supported')
  assert.equal(request.input.dimensions.depth_mm, 100)
})

test('structure adapter names display units and normalizes identifier spelling', () => {
  const model = {
    code: 'Eurocode',
    materials: [{ id: 'M1', name: 'C25', fc: 25, fy: 420, E: 25000 }],
    sections: [{ id: 'S1', name: 'Rect', shape: 'rectRC', params: { bw: 0.3, h: 0.6, cover: 0.04 } }],
    nodes: [{ id: 'N1', x: 0, y: 0, support: 'fix' }, { id: 'N2', x: 5, y: 0, support: 'free' }],
    members: [{
      id: 'B1', n1: 'N1', n2: 'N2', type: 'beam', sectionId: 'S1', materialId: 'M1',
      loads: [{ type: 'D', w: 5 }]
    }],
    slabs: []
  }
  const original = structuredClone(model)
  const request = structureRequest(model)
  assert.equal(request.code_id, 'eurocode')
  assert.equal(request.materials[0].elastic_modulus_mpa, 25000)
  assert.equal(request.sections[0].width_m, 0.3)
  assert.equal(request.nodes[0].support_id, 'fixed')
  assert.equal(request.members[0].loads[0].case_id, 'dead')
  assert.deepEqual(model, original)
})
