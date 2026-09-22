import { useCallback, useEffect, useMemo, useState } from 'react'
import BeamForm from '../components/BeamForm'
import ColumnForm from '../components/ColumnForm'
import SlabForm from '../components/SlabForm'
import StaircaseForm from '../components/StaircaseForm'
import FootingForm from '../components/FootingForm'
import SteelColumnForm from '../components/SteelColumnForm'
import SteelBeamForm from '../components/SteelBeamForm'
import { analyzeElement, downloadBlob, downloadTraceableReport, getCapabilities } from '../api/client'
import { elementCapability, isElementSelectable } from '../api/capabilities'
import CapabilityBadge from '../components/workspace/CapabilityBadge'
import CapabilityPanel from '../components/workspace/CapabilityPanel'
import ReportAction from '../components/workspace/ReportAction'
import { ErrorPanel, LoadingState, StatusNotice } from '../components/workspace/StatusNotice'

const elements = [
  ['beam', 'Beam'], ['column', 'Column'], ['slab', 'Slab'], ['staircase', 'Staircase'], ['footing', 'Footing'], ['steel_beam', 'Steel beam'], ['steel_column', 'Steel column'],
]

function FormForElement({ element, onSubmit, disabled }) {
  const props = { onSubmit, disabled }
  switch (element) {
    case 'beam': return <BeamForm {...props} />
    case 'column': return <ColumnForm {...props} />
    case 'slab': return <SlabForm {...props} />
    case 'staircase': return <StaircaseForm {...props} />
    case 'footing': return <FootingForm {...props} />
    case 'steel_beam': return <SteelBeamForm {...props} />
    case 'steel_column': return <SteelColumnForm {...props} />
    default: return null
  }
}

function ElementResult({ result, reportLoading, onDownload }) {
  if (!result) return <div className="empty-state">Select an available capability route, enter its inputs, and run the analysis.</div>
  if (result.request_status !== 'success') return <ErrorPanel error={result.error} />
  return <div className="result-grid" aria-live="polite">
    <section className="result-section"><div className="section-heading"><div><p className="eyebrow">Analysis completed</p><h2>Element result</h2></div><CapabilityBadge status={result.verification_status} /></div>
      <div className="summary-grid">
        <div className="summary-item"><span>Family</span><strong>{result.code_id}</strong></div>
        <div className="summary-item"><span>Element</span><strong>{result.element_id}</strong></div>
        <div className="summary-item"><span>Analysis run ID</span><strong className="mono">{result.analysis_run_id}</strong></div>
      </div>
      {result.warnings?.length > 0 && <StatusNotice tone="warning" title="Engineering warnings">{result.warnings.map(item => <p key={item}>{item}</p>)}</StatusNotice>}
      <section className="legacy-boundary"><h3>Legacy / Unverified Design Output</h3><p>This retained compatibility output is not an authoritative engineering conclusion. It is kept separate from the server-owned canonical run metadata.</p>
        <details className="raw-details"><summary>Inspect legacy output</summary><pre>{JSON.stringify(result.legacy_unverified, null, 2)}</pre></details></section>
      <details className="raw-details"><summary>Inspect canonical input</summary><pre>{JSON.stringify(result.canonical_input, null, 2)}</pre></details>
      <ReportAction runId={result.analysis_run_id} onDownload={onDownload} loading={reportLoading} />
    </section>
  </div>
}

export default function Analyzer() {
  const [capabilities, setCapabilities] = useState(null)
  const [capabilityError, setCapabilityError] = useState(null)
  const [selectedFamilyId, setSelectedFamilyId] = useState('')
  const [selectedElement, setSelectedElement] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [reportLoading, setReportLoading] = useState(false)

  const loadCapabilities = useCallback(async () => {
    setCapabilityError(null); setCapabilities(null)
    try { const data = await getCapabilities(); setCapabilities(data); setSelectedFamilyId(current => current || data.families[0]?.family_id || '') }
    catch (error) { setCapabilityError(error) }
  }, [])
  useEffect(() => { loadCapabilities() }, [loadCapabilities])

  const family = useMemo(() => capabilities?.families.find(item => item.family_id === selectedFamilyId) || null, [capabilities, selectedFamilyId])
  const capability = elementCapability(family, selectedElement)
  const selectable = isElementSelectable(family, selectedElement)

  const handleFamily = event => { setSelectedFamilyId(event.target.value); setSelectedElement(''); setResult(null) }
  const handleElement = event => { setSelectedElement(event.target.value); setResult(null) }
  const handleSubmit = async formData => {
    if (!family || !selectedElement || !selectable) return
    setLoading(true); setResult(null)
    try { setResult(await analyzeElement({ code: family.family_id, element: selectedElement, formData })) }
    catch (error) { setResult({ request_status: 'error', error }) }
    finally { setLoading(false) }
  }
  const handleReport = async () => {
    if (!result?.analysis_run_id) return
    setReportLoading(true)
    try { downloadBlob(await downloadTraceableReport(result.analysis_run_id), `structicode-${result.analysis_run_id}.pdf`) }
    catch (error) { setResult(current => ({ ...current, error })) }
    finally { setReportLoading(false) }
  }

  return <section><header className="page-header"><div><p className="eyebrow">Element workflow</p><h1>Element Analysis</h1><p>Select a capability-backed route, enter inputs in their displayed contract units, review the explicit verification boundary, then download the server-owned traceable report.</p></div></header>
    {capabilityError && <ErrorPanel error={capabilityError} onRetry={loadCapabilities} />}
    {!capabilities && !capabilityError ? <LoadingState /> : capabilities && <div className="workspace-grid">
      <aside className="workspace-sidebar"><section className="panel control-stack"><h2>1. Select route</h2>
        <label className="field"><span className="field-label">Design-code family</span><select value={selectedFamilyId} onChange={handleFamily}>{capabilities.families.map(item => <option key={item.family_id} value={item.family_id}>{item.display_name} — {item.jurisdiction}</option>)}</select></label>
        <label className="field"><span className="field-label">Element type</span><select value={selectedElement} onChange={handleElement}><option value="">Select an element</option>{elements.map(([id, label]) => { const item = elementCapability(family, id); const enabled = isElementSelectable(family, id); return <option key={id} value={id} disabled={!enabled}>{label} — {item?.status || 'UNKNOWN'}{enabled ? '' : ' (unavailable)'}</option> })}</select></label>
        {capability && <CapabilityBadge status={capability.status} />}
        <StatusNotice tone="warning" title="Seismic workflow"><p>Not implemented in the v1 engineering workflow. No seismic inputs are sent from this page.</p></StatusNotice>
      </section>{family && <CapabilityPanel family={family} capability={capability} element={selectedElement} />}</aside>
      <div className="workspace-content">{selectedElement && !selectable && <StatusNotice tone="warning" title="Route unavailable"><p>{capability?.note || 'This element route is not available for the selected family.'}</p></StatusNotice>}
        {selectedElement && selectable && <section className="panel"><div className="section-heading"><div><p className="eyebrow">2. Input</p><h2>{elements.find(([id]) => id === selectedElement)?.[1]} inputs</h2></div>{capability && <CapabilityBadge status={capability.status} compact />}</div><FormForElement element={selectedElement} onSubmit={handleSubmit} disabled={loading} /></section>}
        {loading && <LoadingState label="Running the validated v1 analysis…" />}<ElementResult result={result} reportLoading={reportLoading} onDownload={handleReport} />
      </div>
    </div>}</section>
}