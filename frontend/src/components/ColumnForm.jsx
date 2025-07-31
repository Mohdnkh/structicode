import { useState } from 'react'

export default function ColumnForm({ onSubmit }) {
  const [type, setType] = useState('Rectangular')
  const [code, setCode] = useState('ACI')
  const [b, setB] = useState('')
  const [h, setH] = useState('')
  const [L, setL] = useState('')
  const [phi, setPhi] = useState('')
  const [nBars, setNBars] = useState('')
  const [s, setS] = useState('')
  const [fc, setFc] = useState('')
  const [fy, setFy] = useState('')
  const [loads, setLoads] = useState({ axial: '', moment: '' })

  const defaultValues = {
    fc: 25,
    fy: 420
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    const data = {
      type,
      code,
      geometry: {
        b: parseFloat(b),
        h: parseFloat(h),
        L: parseFloat(L)
      },
      reinforcement: {
        barDiameter: parseFloat(phi),
        barCount: parseInt(nBars),
        tieSpacing: parseFloat(s)
      },
      materials: {
        fc: parseFloat(fc) || defaultValues.fc,
        fy: parseFloat(fy) || defaultValues.fy
      },
      loads: {
        axial: parseFloat(loads.axial) || 0,
        moment: parseFloat(loads.moment) || 0
      }
    }

    onSubmit(data)
  }

  const columnTypes = ['Rectangular', 'Circular', 'Composite']
  const codes = ['ACI', 'BS', 'Eurocode', 'AS', 'CSA', 'IS', 'Jordan', 'Egypt', 'Saudi', 'UAE', 'Turkey']

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <select value={type} onChange={e => setType(e.target.value)} className="input">
          {columnTypes.map(t => <option key={t}>{t}</option>)}
        </select>

        

        <input type="number" placeholder="Width b (cm)" value={b} onChange={e => setB(e.target.value)} className="input" />
        <input type="number" placeholder="Depth h (cm)" value={h} onChange={e => setH(e.target.value)} className="input" />
        <input type="number" placeholder="Height L (m)" value={L} onChange={e => setL(e.target.value)} className="input" />
        <input type="number" placeholder="Rebar Diameter Φ (mm)" value={phi} onChange={e => setPhi(e.target.value)} className="input" />
        <input type="number" placeholder="Number of Rebars n" value={nBars} onChange={e => setNBars(e.target.value)} className="input" />
        <input type="number" placeholder="Tie Spacing s (cm)" value={s} onChange={e => setS(e.target.value)} className="input" />
        <input type="number" placeholder="Concrete Strength fc (MPa)" value={fc} onChange={e => setFc(e.target.value)} className="input" />
        <input type="number" placeholder="Steel Yield Strength fy (MPa)" value={fy} onChange={e => setFy(e.target.value)} className="input" />
      </div>

      <div className="pt-4 border-t">
        <label className="block mb-2 font-semibold">Loads:</label>
        <div className="grid grid-cols-2 md:grid-cols-2 gap-3">
          <input type="number" placeholder="Axial Load N (kN)" value={loads.axial} onChange={e => setLoads({ ...loads, axial: e.target.value })} className="input" />
          <input type="number" placeholder="Moment M (kN·m)" value={loads.moment} onChange={e => setLoads({ ...loads, moment: e.target.value })} className="input" />
        </div>
      </div>

      <div className="text-center pt-6">
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold">
          Analyze Column
        </button>
      </div>
    </form>
  )
}
