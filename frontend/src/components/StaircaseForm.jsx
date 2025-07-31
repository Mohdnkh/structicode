import { useState } from 'react'

export default function StaircaseForm({ onSubmit }) {
  const [type, setType] = useState('Straight')
  const [b, setB] = useState('')
  const [r, setR] = useState('')
  const [d, setD] = useState('')
  const [n_steps, setNSteps] = useState('')
  const [t, setT] = useState('')
  const [rebar_dia, setRebarDia] = useState('')
  const [fc, setFc] = useState('')
  const [fy, setFy] = useState('')
  const [loads, setLoads] = useState({ dead: '', live: '', wind: '' })
  const [error, setError] = useState('')

  const defaultValues = { fc: 25, fy: 420 }

  const handleSubmit = (e) => {
    e.preventDefault()

    const parsedB = parseFloat(b)
    const parsedR = parseFloat(r)
    const parsedD = parseFloat(d)
    const parsedSteps = parseInt(n_steps)
    const parsedT = parseFloat(t)
    const parsedRebar = parseFloat(rebar_dia)
    const parsedFc = parseFloat(fc) || defaultValues.fc
    const parsedFy = parseFloat(fy) || defaultValues.fy

    if (
      isNaN(parsedB) || isNaN(parsedR) || isNaN(parsedD) ||
      isNaN(parsedSteps) || isNaN(parsedT) || isNaN(parsedRebar)
    ) {
      setError('يرجى تعبئة جميع الحقول بشكل صحيح')
      return
    }

    setError('')

    const data = {
      type,
      width: parsedB,
      riser: parsedR,
      tread: parsedD,
      steps: parsedSteps,
      thickness: parsedT,
      rebar: parsedRebar,
      fc: parsedFc,
      fy: parsedFy,
      loads: {
        dead: parseFloat(loads.dead) || 0,
        live: parseFloat(loads.live) || 0,
        wind: parseFloat(loads.wind) || 0
      }
    }

    onSubmit(data)
  }

  const stairTypes = ['Straight', 'L-Shaped', 'Spiral']

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <select value={type} onChange={e => setType(e.target.value)} className="input">
          {stairTypes.map(t => <option key={t}>{t}</option>)}
        </select>

        <input type="number" placeholder="Stair Width b (cm)" value={b} onChange={e => setB(e.target.value)} className="input" />
        <input type="number" placeholder="Riser Height r (cm)" value={r} onChange={e => setR(e.target.value)} className="input" />
        <input type="number" placeholder="Tread Depth d (cm)" value={d} onChange={e => setD(e.target.value)} className="input" />
        <input type="number" placeholder="Number of Steps n" value={n_steps} onChange={e => setNSteps(e.target.value)} className="input" />
        <input type="number" placeholder="Slab Thickness t (cm)" value={t} onChange={e => setT(e.target.value)} className="input" />
        <input type="number" placeholder="Rebar Diameter φ (mm)" value={rebar_dia} onChange={e => setRebarDia(e.target.value)} className="input" />
        <input type="number" placeholder="Concrete Strength fc (MPa)" value={fc} onChange={e => setFc(e.target.value)} className="input" />
        <input type="number" placeholder="Steel Yield Strength fy (MPa)" value={fy} onChange={e => setFy(e.target.value)} className="input" />
      </div>

      <div className="pt-4 border-t">
        <label className="block mb-2 font-semibold">Loads (kN/m²):</label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <input type="number" placeholder="Dead Load q_dead" value={loads.dead} onChange={e => setLoads({ ...loads, dead: e.target.value })} className="input" />
          <input type="number" placeholder="Live Load q_live" value={loads.live} onChange={e => setLoads({ ...loads, live: e.target.value })} className="input" />
          <input type="number" placeholder="Wind Load q_wind" value={loads.wind} onChange={e => setLoads({ ...loads, wind: e.target.value })} className="input" />
        </div>
      </div>

      {error && <div className="text-red-600 text-center font-semibold">{error}</div>}

      <div className="text-center pt-6">
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold">
          Analyze Staircase
        </button>
      </div>
    </form>
  )
}
