export function Field({ label, hint, children, className = '' }) {
  return <label className={`field ${className}`}><span className="field-label">{label}</span>{children}{hint && <span className="field-hint">{hint}</span>}</label>
}

export function FormSection({ title, children }) {
  return <fieldset className="form-section"><legend>{title}</legend><div className="form-grid">{children}</div></fieldset>
}