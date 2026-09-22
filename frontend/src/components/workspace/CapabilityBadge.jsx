const labels = {
  VERIFIED: 'Verified',
  ENGINEERING_REVIEW_REQUIRED: 'Engineering review required',
  LEGACY_UNVERIFIED: 'Legacy / unverified',
  NOT_IMPLEMENTED: 'Not implemented',
  SOURCE_BLOCKED: 'Source blocked',
  UNVERIFIED: 'Unverified',
  NOT_EVALUATED: 'Not evaluated',
}

export const statusLabel = (status) => labels[status] || status || 'Unknown status'

export default function CapabilityBadge({ status, compact = false }) {
  return <span className={`capability-badge status-${String(status || 'unknown').toLowerCase()}`} aria-label={statusLabel(status)}>
    {!compact && <span className="badge-prefix">Status</span>} {statusLabel(status)} <code>{status}</code>
  </span>
}