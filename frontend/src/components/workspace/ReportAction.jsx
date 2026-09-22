import { Download } from 'lucide-react'

export function canDownloadTraceableReport(runId) { return typeof runId === 'string' && runId.trim().length > 0 }

export default function ReportAction({ runId, onDownload, loading = false }) {
  const enabled = canDownloadTraceableReport(runId) && !loading
  return <div className="report-action">
    <button className="button button-primary" type="button" disabled={!enabled} onClick={onDownload}>
      <Download aria-hidden="true" size={16} /> {loading ? 'Preparing report…' : 'Download Traceable Report'}
    </button>
    <p>Analysis runs and traceable reports are available until the local API restarts. Persistent project history is not available yet.</p>
  </div>
}