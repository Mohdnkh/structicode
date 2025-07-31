import { useState } from 'react'

export default function FootingForm({ onSubmit }) {
  const [type, setType] = useState('Isolated')
  const [L, setL] = useState('')
  const [B, setB] = useState('')
  const [t, setT] = useState('')
  const [P, setP] = useState('')
  const [soilType, setSoilType] = useState('')
  const [phi, setPhi] = useState('')
  const [s, setS] = useState('')
  const [fc, setFc] = useState('')
  const [fy, setFy] = useState('')
  const [error, setError] = useState('')

  const defaultValues = {
    fc: 25,
    fy: 420
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    const parsedL = parseFloat(L)
    const parsedB = parseFloat(B)
    const parsedT = parseFloat(t)
    const parsedP = parseFloat(P)
    const parsedPhi = parseFloat(phi)
    const parsedS = parseFloat(s)
    const parsedFc = parseFloat(fc) || defaultValues.fc
    const parsedFy = parseFloat(fy) || defaultValues.fy

    if (
      isNaN(parsedL) || isNaN(parsedB) || isNaN(parsedT) ||
      isNaN(parsedP) || isNaN(parsedPhi) || isNaN(parsedS) || !soilType
    ) {
      setError('يرجى تعبئة جميع الحقول بشكل صحيح')
      return
    }

    setError('')

    const data = {
      type,
      length: parsedL,
      width: parsedB,
      thickness: parsedT,
      columnLoad: parsedP,
      rebarDiameter: parsedPhi,
      rebarSpacing: parsedS,
      fc: parsedFc,
      fy: parsedFy,
      soilType
    }

    onSubmit(data)
  }

  const footingTypes = ['Isolated', 'Combined', 'Strip', 'Raft']

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <select value={type} onChange={e => setType(e.target.value)} className="input">
          {footingTypes.map(t => <option key={t}>{t}</option>)}
        </select>

        <input type="number" placeholder="Length L (m)" value={L} onChange={e => setL(e.target.value)} className="input" />
        <input type="number" placeholder="Width B (m)" value={B} onChange={e => setB(e.target.value)} className="input" />
        <input type="number" placeholder="Thickness t (cm)" value={t} onChange={e => setT(e.target.value)} className="input" />
        <input type="number" placeholder="Column Load P (kN)" value={P} onChange={e => setP(e.target.value)} className="input" />

        <select value={soilType} onChange={e => setSoilType(e.target.value)} className="input">
          <option value="">-- Select Soil Type --</option>
          <option value="rock">Rock</option>
          <option value="sand">Sand</option>
          <option value="clay">Clay</option>
          <option value="mixed">Mixed</option>
        </select>

        <input type="number" placeholder="Rebar Diameter Φ (mm)" value={phi} onChange={e => setPhi(e.target.value)} className="input" />
        <input type="number" placeholder="Rebar Spacing s (cm)" value={s} onChange={e => setS(e.target.value)} className="input" />
        <input type="number" placeholder="Concrete Strength fc (MPa)" value={fc} onChange={e => setFc(e.target.value)} className="input" />
        <input type="number" placeholder="Steel Yield Strength fy (MPa)" value={fy} onChange={e => setFy(e.target.value)} className="input" />
      </div>

      {error && <div className="text-red-600 text-center font-semibold">{error}</div>}

      <div className="text-center pt-6">
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold">
          Analyze Footing
        </button>
      </div>
    </form>
  )
}
