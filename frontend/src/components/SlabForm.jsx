import { useState } from 'react'

export default function SlabForm({ onSubmit, code }) {
  const [type, setType] = useState('solid')
  const [thickness, setThickness] = useState('')
  const [length, setLength] = useState('')
  const [width, setWidth] = useState('')
  const [fc, setFc] = useState('')
  const [fy, setFy] = useState('')
  const [barDiameter, setBarDiameter] = useState('')
  const [topBarCount, setTopBarCount] = useState('')
  const [bottomBarCount, setBottomBarCount] = useState('')
  const [blockHeight, setBlockHeight] = useState('')
  const [ribWidth, setRibWidth] = useState('')
  const [ribSpacing, setRibSpacing] = useState('')
  const [loads, setLoads] = useState({ dead: '', live: '', wind: '', snow: '' })
  const [error, setError] = useState('')

  const getDefaultValues = (code) => {
    const defaults = {
      ACI: { fc: 28, fy: 420 },
      Eurocode: { fc: 30, fy: 500 },
      BS: { fc: 25, fy: 460 },
      Egypt: { fc: 25, fy: 360 },
      Jordan: { fc: 25, fy: 420 },
      Saudi: { fc: 30, fy: 500 },
      UAE: { fc: 30, fy: 500 },
      IS: { fc: 25, fy: 415 },
      AS: { fc: 32, fy: 500 },
      CSA: { fc: 30, fy: 400 },
      Turkey: { fc: 30, fy: 500 }
    }
    return defaults[code] || { fc: 25, fy: 420 }
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    const parsedT = parseFloat(thickness)
    const parsedL = parseFloat(length)
    const parsedW = parseFloat(width)
    const parsedBarDia = parseFloat(barDiameter)
    const parsedTopBars = parseInt(topBarCount)
    const parsedBottomBars = parseInt(bottomBarCount)

    if (isNaN(parsedT) || isNaN(parsedL) || isNaN(parsedW) || isNaN(parsedBarDia)) {
      setError('يرجى تعبئة الحقول الأساسية وتسليح القطر بشكل صحيح')
      return
    }

    const { fc: defaultFc, fy: defaultFy } = getDefaultValues(code)
    const parsedFc = fc ? parseFloat(fc) : defaultFc
    const parsedFy = fy ? parseFloat(fy) : defaultFy

    const data = {
      type,
      thickness: parsedT,
      length: parsedL,
      width: parsedW,
      fc: parsedFc,
      fy: parsedFy,
      barDiameter: parsedBarDia,
      loads: {
        dead: parseFloat(loads.dead) || 0,
        live: parseFloat(loads.live) || 0,
        wind: parseFloat(loads.wind) || 0,
        snow: parseFloat(loads.snow) || 0
      }
    }

    if (type === 'solid') {
      data.topBarCount = parsedTopBars
      data.bottomBarCount = parsedBottomBars
    }

    if (type === 'hollow') {
      const parsedBlockHeight = parseFloat(blockHeight)
      if (isNaN(parsedBlockHeight)) return setError('يرجى إدخال ارتفاع البلوك')
      data.bottomBarCount = parsedBottomBars
      data.block = { height: parsedBlockHeight }
    }

    if (type === 'waffle') {
      const parsedRibWidth = parseFloat(ribWidth)
      const parsedRibSpacing = parseFloat(ribSpacing)
      if (isNaN(parsedRibWidth) || isNaN(parsedRibSpacing)) {
        return setError('يرجى إدخال أبعاد الريب بشكل صحيح')
      }
      data.bottomBarCount = parsedBottomBars
      data.waffle = {
        ribWidth: parsedRibWidth,
        ribSpacing: parsedRibSpacing
      }
    }

    setError('')
    onSubmit(data)
  }

  const slabTypes = ['solid', 'hollow', 'waffle']

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <select value={type} onChange={e => setType(e.target.value)} className="input">
          {slabTypes.map(t => <option key={t}>{t}</option>)}
        </select>

        <input type="number" placeholder="Thickness t (cm)" value={thickness} onChange={e => setThickness(e.target.value)} className="input" />
        <input type="number" placeholder="Length L (m)" value={length} onChange={e => setLength(e.target.value)} className="input" />
        <input type="number" placeholder="Width B (m)" value={width} onChange={e => setWidth(e.target.value)} className="input" />
        <input type="number" placeholder="Concrete Strength fc (MPa)" value={fc} onChange={e => setFc(e.target.value)} className="input" />
        <input type="number" placeholder="Steel Yield Strength fy (MPa)" value={fy} onChange={e => setFy(e.target.value)} className="input" />
        <input type="number" placeholder="Bar Diameter Φ (mm)" value={barDiameter} onChange={e => setBarDiameter(e.target.value)} className="input" />

        {type === 'solid' && (
          <>
            <input type="number" placeholder="Top Bars Count" value={topBarCount} onChange={e => setTopBarCount(e.target.value)} className="input" />
            <input type="number" placeholder="Bottom Bars Count" value={bottomBarCount} onChange={e => setBottomBarCount(e.target.value)} className="input" />
          </>
        )}

        {type === 'hollow' && (
          <>
            <input type="number" placeholder="Bottom Bars Count" value={bottomBarCount} onChange={e => setBottomBarCount(e.target.value)} className="input" />
            <input type="number" placeholder="Block Height (cm)" value={blockHeight} onChange={e => setBlockHeight(e.target.value)} className="input" />
          </>
        )}

        {type === 'waffle' && (
          <>
            <input type="number" placeholder="Bottom Bars Count" value={bottomBarCount} onChange={e => setBottomBarCount(e.target.value)} className="input" />
            <input type="number" placeholder="Rib Width (cm)" value={ribWidth} onChange={e => setRibWidth(e.target.value)} className="input" />
            <input type="number" placeholder="Rib Spacing (cm)" value={ribSpacing} onChange={e => setRibSpacing(e.target.value)} className="input" />
          </>
        )}
      </div>

      <div className="pt-4 border-t">
        <label className="block mb-2 font-semibold">Loads (kN/m²):</label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <input type="number" placeholder="Dead Load" value={loads.dead} onChange={e => setLoads({ ...loads, dead: e.target.value })} className="input" />
          <input type="number" placeholder="Live Load" value={loads.live} onChange={e => setLoads({ ...loads, live: e.target.value })} className="input" />
          <input type="number" placeholder="Wind Load" value={loads.wind} onChange={e => setLoads({ ...loads, wind: e.target.value })} className="input" />
          <input type="number" placeholder="Snow Load" value={loads.snow} onChange={e => setLoads({ ...loads, snow: e.target.value })} className="input" />
        </div>
      </div>

      {error && <div className="text-red-600 text-center font-semibold">{error}</div>}

      <div className="text-center pt-6">
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold">
          Analyze Slab
        </button>
      </div>
    </form>
  )
}
