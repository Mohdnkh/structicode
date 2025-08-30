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
        body: JSON.stringify({ 
          data: { ...lastInput, code, element }, 
          result: result.result
        })
      })
      if (!res.ok) throw new Error('Failed to generate PDF')
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
      backgroundImage: 'url("/column-load-bg.png")', // ✅ الصورة من public
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

        {/* باقي الكود زي ما هو ... */}

        {result?.status === 'success' && (
          <div style={{ marginTop: '2rem' }}>
            {/* ... */}
            <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
              <button onClick={downloadPDF} style={{
                backgroundColor: '#2563eb',
                color: 'white',
                padding: '10px 24px',
                borderRadius: '12px',
                fontWeight: '600',
                border: 'none',
                cursor: 'pointer',
                position: 'relative',
                zIndex: 10
              }}>
                Download PDF Report
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
