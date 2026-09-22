import { useTranslation } from 'react-i18next'
import CapabilityBadge from './CapabilityBadge'

// The P6 registry remains the only source of these four structure capability values.
export const structureCapabilityFields = [
  ['structure_analysis', 'capability.structure_analysis'],
  ['structure_design', 'capability.structure_design'],
  ['load_combination', 'capability.load_combination'],
  ['seismic', 'capability.seismic'],
]

export default function StructureCapabilitySummary({ family }) {
  const { t } = useTranslation()
  if (!family) return null
  return <section className="capability-panel" aria-labelledby="structure-capability-heading">
    <div className="section-heading"><div><p className="eyebrow">{t('capability.context')}</p><h2 id="structure-capability-heading">{t('capability.structure_summary')}</h2></div></div>
    <dl className="structure-capabilities">
      {structureCapabilityFields.map(([field, label]) => {
        const capability = family[field]
        return <div key={field}>
          <dt>{t(label)}</dt>
          <dd>{capability ? <CapabilityBadge status={capability.status} /> : <span>{t('common.unavailable')}</span>}</dd>
          {capability?.note && <p>{capability.note}</p>}
        </div>
      })}
    </dl>
  </section>
}
