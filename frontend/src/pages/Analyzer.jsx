import { useCallback, useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
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
import { useAuth } from '../context/AuthContext'
import { useProject } from '../context/ProjectContext'
import { projectAnalysisContext } from '../context/projectState'

const elements = ['beam', 'column', 'slab', 'staircase', 'footing', 'steel_beam', 'steel_column']

function FormForElement({ element, onSubmit, disabled }) { const props = { onSubmit, disabled }; return ({ beam:<BeamForm {...props}/>, column:<ColumnForm {...props}/>, slab:<SlabForm {...props}/>, staircase:<StaircaseForm {...props}/>, footing:<FootingForm {...props}/>, steel_beam:<SteelBeamForm {...props}/>, steel_column:<SteelColumnForm {...props}/> })[element] || null }

function ElementResult({ result, reportLoading, reportError, onDownload }) {
  const { t } = useTranslation()
  if (!result) return <div className="empty-state">{t('analyzer.empty')}</div>
  if (result.request_status !== 'success') return <ErrorPanel error={result.error} />
  return <div className="result-grid" aria-live="polite"><section className="result-section"><div className="section-heading"><div><p className="eyebrow">{t('analyzer.completed')}</p><h2>{t('analyzer.result')}</h2></div><CapabilityBadge status={result.verification_status} /></div>
    <div className="summary-grid"><div className="summary-item"><span>{t('analyzer.family_result')}</span><strong><code>{result.code_id}</code></strong></div><div className="summary-item"><span>{t('analyzer.element_result')}</span><strong><code>{result.element_id}</code></strong></div><div className="summary-item"><span>{t('analyzer.run_id')}</span><strong className="mono">{result.analysis_run_id}</strong></div></div>
    {result.warnings?.length > 0 && <StatusNotice tone="warning" title={t('common.warnings')}>{result.warnings.map(item => <p key={item}>{item}</p>)}</StatusNotice>}
    <section className="legacy-boundary"><h3>{t('analyzer.legacy_title')}</h3><p>{t('analyzer.legacy_detail')}</p><details className="raw-details"><summary>{t('analyzer.inspect_legacy')}</summary><pre>{JSON.stringify(result.legacy_unverified, null, 2)}</pre></details></section>
    <details className="raw-details"><summary>{t('analyzer.inspect_input')}</summary><pre>{JSON.stringify(result.canonical_input, null, 2)}</pre></details>
    <StatusNotice tone={result.persistence_state === 'PROJECT_PERSISTED' ? 'success' : 'warning'} title={t(result.persistence_state === 'PROJECT_PERSISTED' ? 'projects.persisted' : 'projects.ephemeral')}><p>{result.persistence_state === 'PROJECT_PERSISTED' ? t('projects.persisted_detail') : t('projects.ephemeral_detail')}</p></StatusNotice>
    <ReportAction runId={result.analysis_run_id} onDownload={onDownload} loading={reportLoading} persistenceState={result.persistence_state} />
    {reportError && <ErrorPanel error={reportError} onRetry={onDownload} />}
  </section></div>
}

export default function Analyzer() {
  const { t } = useTranslation(); const [capabilities, setCapabilities] = useState(null); const [capabilityError, setCapabilityError] = useState(null); const [selectedFamilyId, setSelectedFamilyId] = useState(''); const [selectedElement, setSelectedElement] = useState(''); const [result, setResult] = useState(null); const [loading, setLoading] = useState(false); const [reportLoading, setReportLoading] = useState(false); const [reportError, setReportError] = useState(null)
  const { authenticated } = useAuth(); const { activeProjectId } = useProject()
  const loadCapabilities = useCallback(async () => { setCapabilityError(null); setCapabilities(null); try { const data = await getCapabilities(); setCapabilities(data); setSelectedFamilyId(current => current || data.families[0]?.family_id || '') } catch (error) { setCapabilityError(error) } }, [])
  useEffect(() => { loadCapabilities() }, [loadCapabilities])
  const family = useMemo(() => capabilities?.families.find(item => item.family_id === selectedFamilyId) || null, [capabilities, selectedFamilyId]); const capability = elementCapability(family, selectedElement); const selectable = isElementSelectable(family, selectedElement)
  const handleFamily = event => { setSelectedFamilyId(event.target.value); setSelectedElement(''); setResult(null); setReportError(null) }; const handleElement = event => { setSelectedElement(event.target.value); setResult(null); setReportError(null) }
  const handleSubmit = async formData => { if (!family || !selectedElement || !selectable) return; setLoading(true); setResult(null); setReportError(null); try { setResult(await analyzeElement({ code: family.family_id, element: selectedElement, formData, ...projectAnalysisContext(authenticated, activeProjectId) })) } catch (error) { setResult({ request_status: 'error', error }) } finally { setLoading(false) } }
  const handleReport = async () => { if (!result?.analysis_run_id) return; setReportError(null); setReportLoading(true); try { downloadBlob(await downloadTraceableReport(result.analysis_run_id), `structicode-${result.analysis_run_id}.pdf`) } catch (error) { setReportError(error) } finally { setReportLoading(false) } }
  return <section><header className="page-header"><div><p className="eyebrow">{t('analyzer.eyebrow')}</p><h1>{t('analyzer.title')}</h1><p>{t('analyzer.subtitle')}</p></div></header>
    {capabilityError && <ErrorPanel error={capabilityError} onRetry={loadCapabilities} />}{!capabilities && !capabilityError ? <LoadingState /> : capabilities && <div className="workspace-grid"><aside className="workspace-sidebar"><section className="panel control-stack"><h2>{t('analyzer.select_route')}</h2>
      <label className="field"><span className="field-label">{t('analyzer.family')}</span><select value={selectedFamilyId} onChange={handleFamily}>{capabilities.families.map(item => <option key={item.family_id} value={item.family_id}>{item.display_name} — {item.jurisdiction}</option>)}</select></label>
      <label className="field"><span className="field-label">{t('analyzer.element')}</span><select value={selectedElement} onChange={handleElement}><option value="">{t('analyzer.select_element')}</option>{elements.map(id => { const item = elementCapability(family, id); const enabled = isElementSelectable(family, id); return <option key={id} value={id} disabled={!enabled}>{t(`elements.${id}`)} — {item?.status || 'UNKNOWN'}{enabled ? '' : ` (${t('common.unavailable')})`}</option> })}</select></label>
      {capability && <CapabilityBadge status={capability.status} />}<StatusNotice tone="warning" title={t('analyzer.seismic_title')}><p>{t('analyzer.seismic_notice')}</p></StatusNotice>
    </section>{family && <CapabilityPanel family={family} capability={capability} element={selectedElement} />}</aside>
    <div className="workspace-content">{selectedElement && !selectable && <StatusNotice tone="warning" title={t('analyzer.route_unavailable')}><p>{capability?.note || t('analyzer.route_unavailable_notice')}</p></StatusNotice>}{selectedElement && selectable && <section className="panel"><div className="section-heading"><div><p className="eyebrow">{t('analyzer.input')}</p><h2>{t('analyzer.inputs', { element: t(`elements.${selectedElement}`) })}</h2></div>{capability && <CapabilityBadge status={capability.status} compact />}</div><FormForElement element={selectedElement} onSubmit={handleSubmit} disabled={loading} /></section>}{loading && <LoadingState label={t('analyzer.running')} />}<ElementResult result={result} reportLoading={reportLoading} reportError={reportError} onDownload={handleReport} /></div>
  </div>}</section>
}
