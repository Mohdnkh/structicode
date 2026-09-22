const ROUTABLE_STATUSES = new Set(['VERIFIED', 'ENGINEERING_REVIEW_REQUIRED', 'LEGACY_UNVERIFIED'])

export function isCapabilityResponse(value) {
  return Boolean(value && Array.isArray(value.families) && value.families.every(family =>
    typeof family.family_id === 'string' && Array.isArray(family.element_capabilities)))
}

export function elementCapability(family, elementId) {
  return family?.element_capabilities?.find(item => item.element_id === elementId)?.capability || null
}

export function isElementSelectable(family, elementId) {
  const capability = elementCapability(family, elementId)
  return Boolean(capability?.v1_route && ROUTABLE_STATUSES.has(capability.status))
}

export function structureCapability(family) { return family?.structure_analysis || null }

export function isStructureSelectable(family) {
  const capability = structureCapability(family)
  return Boolean(capability?.v1_route && ROUTABLE_STATUSES.has(capability.status))
}

export function sourceBlockedTargets(family) {
  return (family?.verification_targets || []).filter(target => target.status === 'SOURCE_BLOCKED')
}

export function capabilityWarning(capability) {
  if (!capability) return 'Capability metadata is unavailable.'
  if (capability.status === 'NOT_IMPLEMENTED') return 'This route is not implemented in the v1 engineering workflow.'
  if (capability.status === 'SOURCE_BLOCKED') return 'This future verification target is source blocked and is not an active route.'
  if (capability.status === 'LEGACY_UNVERIFIED') return 'This legacy route is available but its engineering output is unverified.'
  if (capability.status === 'ENGINEERING_REVIEW_REQUIRED') return 'This mechanics workflow requires engineering review.'
  return capability.note || ''
}