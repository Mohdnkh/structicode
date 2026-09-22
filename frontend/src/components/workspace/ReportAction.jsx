import { Download } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export function canDownloadTraceableReport(runId) { return typeof runId === 'string' && runId.trim().length > 0 }
export function reportNoticeKey(persistenceState) { return persistenceState === 'PROJECT_PERSISTED' ? 'report.persisted' : 'report.ephemeral' }

export default function ReportAction({ runId, onDownload, loading = false, persistenceState = 'EPHEMERAL' }) {
  const { t } = useTranslation()
  const enabled = canDownloadTraceableReport(runId) && !loading
  return <div className="report-action">
    <button className="button button-primary" type="button" disabled={!enabled} onClick={onDownload}>
      <Download aria-hidden="true" size={16} /> {loading ? t('report.preparing') : t('report.download')}
    </button>
    <p>{t(reportNoticeKey(persistenceState))}</p>
  </div>
}
