import { useState } from 'react'
import BeamForm from '../components/BeamForm'
import ColumnForm from '../components/ColumnForm'
import SlabForm from '../components/SlabForm'
import StaircaseForm from '../components/StaircaseForm'
import FootingForm from '../components/FootingForm'
import SteelColumnForm from '../components/SteelColumnForm'
import SteelBeamForm from '../components/SteelBeamForm'

export default function Analyzer() {
  const [code, setCode] = useState('')
  const [element, setElement] = useState('')
  const [result, setResult] = useState(null)
  const [seismic, setSeismic] = useState({ zone: '', soil: '', importance: '', system: '' })
  const [loading, setLoading] = useState(false)
  const [lastInput, setLastInput] = useState(null)

  const codes = ['ACI', 'BS', 'Eurocode', 'AS', 'CSA', 'IS', 'Jordan', 'Egypt', 'Saudi', 'UAE', 'Turkey']
  const concreteElements = [
    { label: 'Beam', value: 'beam' },
    { label: 'Column', value: 'column' },
    { label: 'Slab', value: 'slab' },
    { label: 'Staircase', value: 'staircase' },
    { label: 'Footing', value: 'footing' }
  ]
  const steelElements = [
    { label: 'Steel Beam', value: 'steel_beam' },
    { label: 'Steel Column', value: 'steel_column' }
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
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const json = await response.json()
      setResult(json)
    } catch (error) {
      setResult({ status: 'error', message: 'Failed to analyze. Please check server connection.' })
    } finally {
      setLoading(false)
    }
  }

  const downloadPDF = async () => {
    if (!lastInput || !result) return
    try {
      const res = await fetch('/generate-pdf', {
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
    <div style={{ minHeight: '100vh', backgroundImage: 'url("/column-load-bg.png")', backgroundSize: 'cover', backgroundPosition: 'center', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '40px 20px' }}>
      <div style={{ maxWidth: '800px', width: '100%', backgroundColor: 'rgba(255, 255, 255, 0.95)', padding: '40px', borderRadius: '20px', boxShadow: '0 8px 16px rgba(0, 0, 0, 0.1)' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '2rem', textAlign: 'center' }}>
          Structural Element Analysis
        </h2>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Select Design Code:</label>
          <select value={code} onChange={e => setCode(e.target.value)} className="input">
            <option value="">-- Select Design Code --</option>
            {codes.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        {[['Concrete Elements', concreteElements], ['Steel Elements', steelElements]].map(([label, list]) => (
          <div key={label} style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>{label}:</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {list.map(el => (
                <button key={el.value} onClick={() => setElement(el.value)} style={{ padding: '10px 16px', borderRadius: '10px', border: '1px solid #ccc', fontWeight: '600', backgroundColor: element === el.value ? '#2563eb' : '#f3f4f6', color: element === el.value ? 'white' : '#111', cursor: 'pointer' }}>
                  {el.label}
                </button>
              ))}
            </div>
          </div>
        ))}

        {code && (
          <div style={{ marginTop: '2rem' }}>
            <h4 style={{ fontWeight: 'bold', fontSize: '1.125rem', marginBottom: '1rem' }}>
              Seismic Parameters
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ fontWeight: 500 }}>Seismic Zone:</label>
                <select value={seismic.zone} onChange={(e) => setSeismic({ ...seismic, zone: e.target.value })} className="input">
                  <option value="">-- Select Zone --</option>
                  {seismicZones.map(zone => (
                    <option key={zone} value={zone}>{zone}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Soil Type:</label>
                <select value={seismic.soil} onChange={(e) => setSeismic({ ...seismic, soil: e.target.value })} className="input">
                  <option value="">-- Select --</option>
                  <option value="rock">Rock</option>
                  <option value="medium">Medium</option>
                  <option value="soft">Soft</option>
                </select>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Importance Category:</label>
                <select value={seismic.importance} onChange={(e) => setSeismic({ ...seismic, importance: e.target.value })} className="input">
                  <option value="">-- Select --</option>
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>System Type:</label>
                <select value={seismic.system} onChange={(e) => setSeismic({ ...seismic, system: e.target.value })} className="input">
                  <option value="">-- Select --</option>
                  <option value="moment_frame">Moment Frame</option>
                  <option value="shear_wall">Shear Wall</option>
                  <option value="dual">Dual System</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {code && element && (
          <>
            <h4 style={{ fontWeight: 'bold', fontSize: '1.125rem', margin: '2rem 0 1rem' }}>
              Structural Parameters
            </h4>
            {renderForm()}
          </>
        )}

        {loading && <p style={{ marginTop: '2rem', textAlign: 'center', color: '#2563eb' }}>Analyzing...</p>}

        {result && result.status === 'success' && (
          <div style={{ marginTop: '2rem', borderTop: '1px solid #ccc', paddingTop: '1.5rem' }}>
            <div style={{ marginBottom: '2rem' }}>
              <h4 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#059669', marginBottom: '0.5rem' }}>
                ✅ Structural Check: {result.result?.structural?.status === 'safe' ? 'Safe' : 'Unsafe'}
              </h4>
              <ul style={{ backgroundColor: '#f0fdf4', padding: '12px', borderRadius: '8px' }}>
                {Object.entries(result.result?.structural || {}).map(([key, value]) => {
                  if (key === 'details' || key === 'recommendations') return null
                  return (
                    <li key={key}>
                      <strong>{key}:</strong>{' '}
                      {typeof value === 'object' ? (
                        <ul style={{ marginLeft: '1rem' }}>
                          {Object.entries(value).map(([k, v]) => (
                            <li key={k}><strong>{k}:</strong> {v}</li>
                          ))}
                        </ul>
                      ) : value}
                    </li>
                  )
                })}
                {result.result?.structural?.details && (
                  <>
                    <li><strong>Details:</strong></li>
                    <ul style={{ marginLeft: '1rem' }}>
                      {Object.entries(result.result.structural.details).map(([k, v]) => (
                        <li key={k}><strong>{k}:</strong> {v}</li>
                      ))}
                    </ul>
                  </>
                )}
                {result.result?.structural?.recommendations?.length > 0 && (
                  <>
                    <li><strong>Recommendations:</strong></li>
                    <ul style={{ marginLeft: '1rem' }}>
                      {result.result.structural.recommendations.map((rec, i) => (
                        <li key={i}>- {rec}</li>
                      ))}
                    </ul>
                  </>
                )}
              </ul>
            </div>
            {result.result?.seismic && (
              <div>
                <h4 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#2563eb', marginBottom: '0.5rem' }}>
                  🌐 Seismic Check: {result.result.seismic?.status}
                </h4>
                <ul style={{ backgroundColor: '#eff6ff', padding: '12px', borderRadius: '8px' }}>
                  {Object.entries(result.result.seismic).map(([key, value]) => (
                    <li key={key}><strong>{key}:</strong> {value}</li>
                  ))}
                </ul>
              </div>
            )}
            <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
              <button onClick={downloadPDF} style={{ backgroundColor: '#1d4ed8', color: 'white', padding: '10px 24px', borderRadius: '12px', fontWeight: '600', border: 'none', cursor: 'pointer' }}>
                Download PDF Report
              </button>
            </div>
          </div>
        )}

        {result && result.status === 'error' && (
          <p style={{ color: 'red', fontWeight: '600' }}>❌ {result.message}</p>
        )}
      </div>
    </div>
  )
}
