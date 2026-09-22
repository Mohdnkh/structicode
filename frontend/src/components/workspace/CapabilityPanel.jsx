import CapabilityBadge from './CapabilityBadge'

export default function CapabilityPanel({ family, capability, element }) {
  if (!family) return null
  const targets = family.verification_targets || []
  return <section className="capability-panel" aria-labelledby="capability-heading">
    <div className="section-heading"><div><p className="eyebrow">Capability context</p><h2 id="capability-heading">{family.display_name}</h2></div>
      {capability && <CapabilityBadge status={capability.status} />}</div>
    <dl className="metadata-grid">
      <div><dt>Jurisdiction</dt><dd>{family.jurisdiction}</dd></div>
      <div><dt>Metadata confidence</dt><dd>{family.standard_metadata?.confidence || 'UNKNOWN'}</dd></div>
      {element && <div><dt>Element route</dt><dd>{element}</dd></div>}
    </dl>
    {capability?.note && <p className="capability-note">{capability.note}</p>}
    {family.warnings?.length > 0 && <ul className="notice-list">{family.warnings.map(item => <li key={item}>{item}</li>)}</ul>}
    {targets.length > 0 && <div className="source-targets"><strong>Future verification targets — source blocked</strong>
      {targets.map(target => <p key={target.target_id}><code>{target.target_id}</code>: {target.source_requirements?.join('; ')}</p>)}</div>}
  </section>
}