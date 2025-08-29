import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import BeamForm from '../components/BeamForm'
import ColumnForm from '../components/ColumnForm'
import SlabForm from '../components/SlabForm'
import StaircaseForm from '../components/StaircaseForm'
import FootingForm from '../components/FootingForm'
import SteelColumnForm from '../components/SteelColumnForm'
import SteelBeamForm from '../components/SteelBeamForm'
import { useTranslation } from 'react-i18next'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function Analyzer() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const [code, setCode] = useState('')
  const [element, setElement] = useState('')
  const [result, setResult] = useState(null)
  const [seismic, setSeismic] = useState({ zone: '', soil: '', importance: '', system: '' })
  const [loading, setLoading] = useState(false)
  const [lastInput, setLastInput] = useState(null)

  useEffect(() => {
    document.documentElement.dir = i18n.language === 'ar' ? 'rtl' : 'ltr'
  }, [i18n.language])

  const codes = ['ACI', 'BS', 'Eurocode', 'AS', 'CSA', 'IS', 'Jordan', 'Egypt', 'Saudi', 'UAE', 'Turkey']
  const concreteElements = [
    { label: t('analyzer.beam'), value: 'beam' },
    { label: t('analyzer.column'), value: 'column' },
    { label: t('analyzer.slab'), value: 'slab' },
    { label: t('analyzer.staircase'), value: 'staircase' },
    { label: t('analyzer.footing'), value: 'footing' }
  ]
  const steelElements = [
    { label: t('analyzer.steel_beam'), value: 'steel_beam' },
    { label: t('analyzer.steel_column'), value: 'steel_column' }
  ]

  const zoneOptionsMap = {
    Jordan: ['1', '2A', '2B', '3'],
    Egypt: ['1', '2', '3'],
    Saudi: ['A', 'B', 'C', 'D1', 'D2'],
    UAE: ['Zone 0', 'Zone 1', 'Zone 2A', 'Zone 2B'],
    Turkey: ['1', '2', '3', '4'],
    Eurocode: ['low', 'medium', 'high'],
    ACI: ['1', '2', '3', '4'],
    AS: ['A', 'B', 'C', 'D'],
    CSA: ['low', 'medium', 'high'],
    IS: ['II', 'III', 'IV', 'V'],
    BS: ['low', 'moderate', 'high']
  }

  const handleSubmit = async (formData) => {
    setLoading(true)
    setResult(null)
    setLastInput(formData)

    const payload = {
      code,
      element,
      data: formData,
      seismic: seismic.zone ? seismic : null
    }

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const json = await response.json()
      setResult(json)
    } catch (error) {
      console.error('Analyze Error:', error)
      setResult({ status: 'error', message: 'Failed to analyze. Please check server connection.' })
    } finally {
      setLoading(false)
    }
  }

  const downloadPDF = async () => {
    if (!lastInput || !result) return
    try {
      const res = await fetch(`${API_BASE}/generate-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: { ...lastInput, code, element }, result })
      })
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'analysis_report.pdf'
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('PDF Download Error:', err)
    }
  }

  const renderForm = () => {
    switch (element) {
      case 'beam': return <BeamForm onSubmit={handleSubmit} />
      case 'column': return <ColumnForm onSubmit={handleSubmit} />
      case 'slab': return <SlabForm onSubmit={handleSubmit} code={code} />
      case 'staircase': return <StaircaseForm onSubmit={handleSubmit} />
      case 'footing': return <FootingForm onSubmit={handleSubmit} />
      case 'steel_column': return <SteelColumnForm onSubmit={handleSubmit} />
      case 'steel_beam': return <SteelBeamForm onSubmit={handleSubmit} />
      default: return null
    }
  }

  const seismicZones = zoneOptionsMap[code] || []

  return (
    <div style={{
      minHeight: '100vh',
      backgroundImage: 'url("/column-load-bg.png")',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      padding: '40px'
    }}>
      <div style={{
        maxWidth: '880px',
        margin: 'auto',
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '20px',
        boxShadow: '0 8px 16px rgba(0, 0, 0, 0.1)'
      }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>{t('home.title')}</h2>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ fontWeight: 600 }}>{t('analyzer.select_code')}</label>
          <select value={code} onChange={e => setCode(e.target.value)} className="input">
            <option value="">-- {t('analyzer.select_code')} --</option>
            {codes.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        {/* ✅ زر الانتقال لتحليل الهيكل الكامل */}
        <div style={{ marginBottom: '2rem' }}>
          <label style={{ fontWeight: 600 }}>{t('analyzer.structure')}</label>
          <div>
            <button
              onClick={() => navigate('/structure-designer')}
              style={{
                padding: '10px 16px',
                borderRadius: '10px',
                border: '1px solid #ccc',
                fontWeight: '600',
                backgroundColor: '#f3f4f6',
                color: '#111',
                cursor: 'pointer',
                marginTop: '8px'
              }}
            >
              {t('analyzer.structure_analysis')}
            </button>
          </div>
        </div>

        {code && (
          <div style={{ marginBottom: '2rem' }}>
            <h4 style={{ fontWeight: 'bold', fontSize: '1.125rem', marginBottom: '1rem' }}>{t('analyzer.seismic')}</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label>{t('analyzer.zone')}</label>
                <select value={seismic.zone} onChange={(e) => setSeismic({ ...seismic, zone: e.target.value })}>
                  <option value="">-- {t('analyzer.zone')} --</option>
                  {seismicZones.map(zone => <option key={zone} value={zone}>{zone}</option>)}
                </select>
              </div>
              <div>
                <label>{t('analyzer.soil')}</label>
                <select value={seismic.soil} onChange={(e) => setSeismic({ ...seismic, soil: e.target.value })}>
                  <option value="">-- {t('analyzer.soil')} --</option>
                  <option value="rock">{t('analyzer.rock')}</option>
                  <option value="medium">{t('analyzer.medium')}</option>
                  <option value="soft">{t('analyzer.soft')}</option>
                </select>
              </div>
              <div>
                <label>{t('analyzer.importance')}</label>
                <select value={seismic.importance} onChange={(e) => setSeismic({ ...seismic, importance: e.target.value })}>
                  <option value="">-- {t('analyzer.importance')} --</option>
                  <option value="low">{t('analyzer.low')}</option>
                  <option value="normal">{t('analyzer.normal')}</option>
                  <option value="high">{t('analyzer.high')}</option>
                </select>
              </div>
              <div>
                <label>{t('analyzer.system')}</label>
                <select value={seismic.system} onChange={(e) => setSeismic({ ...seismic, system: e.target.value })}>
                  <option value="">-- {t('analyzer.system')} --</option>
                  <option value="moment_frame">{t('analyzer.moment_frame')}</option>
                  <option value="shear_wall">{t('analyzer.shear_wall')}</option>
                  <option value="dual">{t('analyzer.dual')}</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {[['analyzer.concrete', concreteElements], ['analyzer.steel', steelElements]].map(([label, list]) => (
          <div key={label} style={{ marginBottom: '1.5rem' }}>
            <label>{t(label)}</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {list.map(el => (
                <button key={el.value} onClick={() => setElement(el.value)} style={{
                  padding: '10px 16px',
                  borderRadius: '10px',
                  border: '1px solid #ccc',
                  fontWeight: '600',
                  backgroundColor: element === el.value ? '#2563eb' : '#f3f4f6',
                  color: element === el.value ? 'white' : '#111',
                  cursor: 'pointer'
                }}>
                  {el.label}
                </button>
              ))}
            </div>
          </div>
        ))}

        {code && element && renderForm()}

        {loading && <p style={{ textAlign: 'center', color: '#2563eb' }}>{t('analyzer.loading')}</p>}

        {result?.status === 'success' && (
          <div style={{ marginTop: '2rem' }}>
            <div style={{
              backgroundColor: result.result.structural?.status === 'safe' ? '#e6f4ea' : '#fde8e8',
              padding: '12px 16px',
              borderRadius: '8px',
              marginBottom: '1rem'
            }}>
              <h3>Structural Check: {result.result.structural?.status}</h3>
            </div>

            <ul style={{ background: '#f3f4f6', padding: '16px', borderRadius: '8px' }}>
              {Object.entries(result.result.structural || {}).map(([key, val]) => (
                key !== 'details' && key !== 'recommendations' && <li key={key}><strong>{key}:</strong> {JSON.stringify(val)}</li>
              ))}
            </ul>

            {result.result.structural?.details && (
              <>
                <h4>Details:</h4>
                <ul>
                  {Object.entries(result.result.structural.details).map(([k, v]) => (
                    <li key={k}><strong>{k}:</strong> {v}</li>
                  ))}
                </ul>
              </>
            )}

            {result.result.structural?.recommendations?.length > 0 && (
              <>
                <h4>Recommendations:</h4>
                <ul>
                  {result.result.structural.recommendations.map((rec, i) => (
                    <li key={i}>- {rec}</li>
                  ))}
                </ul>
              </>
            )}

            {result.result.seismic && (
              <>
                <h3 style={{ marginTop: '2rem' }}>Seismic Check</h3>
                <ul style={{ background: '#e0f2fe', padding: '16px', borderRadius: '8px' }}>
                  {Object.entries(result.result.seismic).map(([key, val]) => (
                    <li key={key}><strong>{key}:</strong> {val}</li>
                  ))}
                </ul>
              </>
            )}

            <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
              <button onClick={downloadPDF} style={{
                backgroundColor: '#2563eb',
                color: 'white',
                padding: '10px 24px',
                borderRadius: '12px',
                fontWeight: '600',
                border: 'none',
                cursor: 'pointer'
              }}>
                Download PDF Report
              </button>
            </div>
          </div>
        )}

        {result?.status === 'error' && (
          <p style={{ color: 'red', fontWeight: '600' }}>❌ {result.message}</p>
        )}
      </div>
    </div>
  )
}
