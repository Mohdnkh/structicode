// Form values retain their displayed units. Field suffixes carry those units to v1.
const loadCases = { D: 'dead', L: 'live', W: 'wind', S: 'snow', E: 'earthquake' }

export const codeId = (value) => String(value).trim().toLowerCase()

export function elementRequest({ code, element, formData, seismic }) {
  const common = { code_id: codeId(code) }
  let input
  switch (element) {
    case 'beam':
      input = {
        kind: 'beam', beam_type: formData.type.toLowerCase(),
        width_cm: formData.width, depth_cm: formData.depth, span_m: formData.length,
        cover_cm: formData.cover, fc_mpa: formData.fc, fy_mpa: formData.fy,
        bar_count: formData.rebar.count, bar_diameter_mm: formData.rebar.diameter,
        line_loads_kn_per_m: formData.loads
      }
      break
    case 'column':
      input = {
        kind: 'column', column_type: formData.type.toLowerCase(),
        width_cm: formData.geometry.b, depth_cm: formData.geometry.h,
        height_m: formData.geometry.L,
        bar_diameter_mm: formData.reinforcement.barDiameter,
        bar_count: formData.reinforcement.barCount,
        tie_spacing_cm: formData.reinforcement.tieSpacing,
        fc_mpa: formData.materials.fc, fy_mpa: formData.materials.fy,
        axial_force_kn: formData.loads.axial, moment_kn_m: formData.loads.moment
      }
      break
    case 'slab':
      input = {
        kind: 'slab', slab_type: formData.type,
        thickness_cm: formData.thickness, length_m: formData.length,
        width_m: formData.width, fc_mpa: formData.fc, fy_mpa: formData.fy,
        bar_diameter_mm: formData.barDiameter,
        bottom_bar_count: formData.bottomBarCount,
        area_loads_kn_per_m2: formData.loads
      }
      if (formData.type === 'solid') input.top_bar_count = formData.topBarCount
      if (formData.type === 'hollow') input.block_height_cm = formData.block?.height
      if (formData.type === 'waffle') {
        input.rib_width_cm = formData.waffle?.ribWidth
        input.rib_spacing_cm = formData.waffle?.ribSpacing
      }
      break
    case 'footing':
      input = {
        kind: 'footing', footing_type: formData.type.toLowerCase(),
        length_m: formData.length, width_m: formData.width,
        thickness_cm: formData.thickness,
        axial_force_kn: formData.columnLoad,
        bar_diameter_mm: formData.rebarDiameter,
        bar_spacing_cm: formData.rebarSpacing,
        fc_mpa: formData.fc, fy_mpa: formData.fy,
        soil_type: formData.soilType
      }
      break
    case 'staircase':
      input = {
        kind: 'staircase', stair_type: formData.type.toLowerCase(),
        width_cm: formData.width, riser_cm: formData.riser,
        tread_cm: formData.tread, steps: formData.steps,
        thickness_cm: formData.thickness, bar_diameter_mm: formData.rebar,
        fc_mpa: formData.fc, fy_mpa: formData.fy,
        area_loads_kn_per_m2: formData.loads
      }
      break
    case 'steel_beam':
      input = {
        kind: 'steel_beam', section_type: formData.sectionType,
        section_size: formData.sectionSize,
        dimensions: steelDimensions(formData.dimensions),
        fy_mpa: formData.steelGrade, span_mm: formData.span,
        uniform_load_kn_per_m: formData.uniformLoad,
        support_type: formData.supportType === 'Simply Supported'
          ? 'simply_supported' : formData.supportType.toLowerCase()
      }
      break
    case 'steel_column':
      input = {
        kind: 'steel_column', section_type: formData.sectionType,
        section_size: formData.sectionSize,
        dimensions: steelDimensions(formData.dimensions),
        fy_mpa: formData.steelGrade, axial_force_kn: formData.axialLoad,
        length_mm: formData.length, k_factor: formData.kFactor,
        boundary_condition: formData.boundaryCondition
      }
      break
    default:
      throw new Error(`Unsupported element identifier: ${element}`)
  }
  return { ...common, input, ...(seismic?.zone ? { seismic } : {}) }
}

function steelDimensions(dimensions) {
  return {
    depth_mm: Number(dimensions.depth), width_mm: Number(dimensions.width),
    flange_thickness_mm: Number(dimensions.flangeThickness),
    web_thickness_mm: Number(dimensions.webThickness)
  }
}

export function structureRequest(model) {
  return {
    code_id: codeId(model.code),
    materials: model.materials.map(material => ({
      id: material.id, name: material.name,
      fc_mpa: material.fc, fy_mpa: material.fy,
      elastic_modulus_mpa: material.E
    })),
    sections: model.sections.map(section => ({
      id: section.id, name: section.name, shape: section.shape,
      width_m: section.params.bw, depth_m: section.params.h,
      cover_m: section.params.cover,
      ...(section.params.A === undefined ? {} : { area_m2: section.params.A })
    })),
    nodes: model.nodes.map(node => ({
      id: node.id, x_m: node.x, y_m: node.y,
      support_id: node.support === 'fix' ? 'fixed' : node.support
    })),
    members: model.members.map(member => ({
      id: member.id, n1: member.n1, n2: member.n2,
      member_type: member.type, section_id: member.sectionId,
      material_id: member.materialId,
      loads: (member.loads || []).map(load => ({
        case_id: loadCases[load.type] || load.type,
        line_load_kn_per_m: load.w
      }))
    })),
    slabs: model.slabs.map(slab => ({
      id: slab.id, x_m: slab.x, y_m: slab.y,
      width_m: slab.w, height_m: slab.h, thickness_m: slab.t,
      material_id: slab.materialId
    }))
  }
}
