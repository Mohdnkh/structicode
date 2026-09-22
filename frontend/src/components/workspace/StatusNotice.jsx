import { AlertTriangle, CircleAlert, Info, LoaderCircle } from 'lucide-react'

export function StatusNotice({ tone = 'info', title, children, live = false }) {
  const Icon = tone === 'error' ? CircleAlert : tone === 'warning' ? AlertTriangle : Info
  return <section className={`status-notice notice-${tone}`} role={tone === 'error' ? 'alert' : 'status'} aria-live={live ? 'polite' : undefined}>
    <Icon aria-hidden="true" size={18} /><div><strong>{title}</strong>{children && <div>{children}</div>}</div>
  </section>
}

export function LoadingState({ label = 'Loading workspace capability data…' }) {
  return <div className="loading-state" role="status" aria-live="polite"><LoaderCircle className="spin" aria-hidden="true" size={18} /> {label}</div>
}

export function ErrorPanel({ error, onRetry }) {
  return <StatusNotice tone="error" title={error?.code || 'Workspace unavailable'} live>
    <p>{error?.message || 'The local API did not return usable capability metadata.'}</p>
    {error?.details?.length > 0 && <ul>{error.details.map((item, index) => <li key={`${item.field}-${index}`}>{item.field}: {item.message}</li>)}</ul>}
    {onRetry && <button className="button button-secondary" type="button" onClick={onRetry}>Retry</button>}
  </StatusNotice>
}