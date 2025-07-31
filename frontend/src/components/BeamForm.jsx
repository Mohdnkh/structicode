import { useState } from 'react'

export default function BeamForm({ onSubmit }) {
  const [type, setType] = useState('Normal')
  const [code, setCode] = useState('ACI')
  const [fc, setFc] = useState('')
  const [fy, setFy] = useState('')
  const [width, setWidth] = useState('')
  const [depth, setDepth] = useState('')
  const [length, setLength] = useState('')
  const [cover, setCover] = useState('3')
  const [rebarCount, setRebarCount] = useState('')
  const [rebarDiameter, setRebarDiameter] = useState('')
  const [loads, setLoads] = useState({ dead: '', live: '', wind: '', snow: '' })

  const defaultValues = {
    fc: 25,
    fy: 420
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    const parsedData = {
      type,
      code,
      fc: parseFloat(fc) || defaultValues.fc,
      fy: parseFloat(fy) || defaultValues.fy,
      width: parseFloat(width),
      depth: parseFloat(depth),
      length: parseFloat(length),
      cover: parseFloat(cover),
      rebar: {
        count: parseInt(rebarCount),
        diameter: parseFloat(rebarDiameter)
      },
      loads: {
        dead: parseFloat(loads.dead) || 0,
        live: parseFloat(loads.live) || 0,
        wind: parseFloat(loads.wind) || 0,
        snow: parseFloat(loads.snow) || 0
      }
    }

    onSubmit(parsedData)
  }

  const beamTypes = ['Normal', 'Inverted', 'Tee', 'Prestressed']
  const codes = ['ACI', 'BS', 'Eurocode', 'AS', 'CSA', 'IS', 'Jordan', 'Egypt', 'Saudi', 'UAE', 'Turkey']

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <select value={type} onChange={e => setType(e.target.value)} className="input">
          {beamTypes.map(t => <option key={t}>{t}</option>)}
        </select>

        

        <input type="number" step="0.01" placeholder="Concrete Strength fc (MPa)" value={fc} onChange={e => setFc(e.target.value)} className="input" />
        <input type="number" step="0.01" placeholder="Steel Yield Strength fy (MPa)" value={fy} onChange={e => setFy(e.target.value)} className="input" />
        <input type="number" step="0.01" placeholder="Beam Width b (cm)" value={width} onChange={e => setWidth(e.target.value)} className="input" />
        <input type="number" step="0.01" placeholder="Beam Depth h (cm)" value={depth} onChange={e => setDepth(e.target.value)} className="input" />
        <input type="number" step="0.01" placeholder="Beam Length L (m)" value={length} onChange={e => setLength(e.target.value)} className="input" />
        <input type="number" placeholder="Number of Rebars n" value={rebarCount} onChange={e => setRebarCount(e.target.value)} className="input" />
        <input type="number" placeholder="Bar Diameter ϕ (mm)" value={rebarDiameter} onChange={e => setRebarDiameter(e.target.value)} className="input" />
        <input type="number" step="0.1" placeholder="Concrete Cover (cm)" value={cover} onChange={e => setCover(e.target.value)} className="input" />
      </div>

      <div className="pt-4 border-t">
        <label className="block mb-2 font-semibold">Loads (kN/m):</label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <input type="number" placeholder="Dead Load" value={loads.dead} onChange={e => setLoads({ ...loads, dead: e.target.value })} className="input" />
          <input type="number" placeholder="Live Load" value={loads.live} onChange={e => setLoads({ ...loads, live: e.target.value })} className="input" />
          <input type="number" placeholder="Wind Load" value={loads.wind} onChange={e => setLoads({ ...loads, wind: e.target.value })} className="input" />
          <input type="number" placeholder="Snow Load" value={loads.snow} onChange={e => setLoads({ ...loads, snow: e.target.value })} className="input" />
        </div>
      </div>

      <div className="text-center pt-6">
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold">
          Analyze Beam
        </button>
      </div>
    </form>
  )
}