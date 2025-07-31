import { useState, useEffect } from 'react'
import sectionData from '../data/steel_sections_data.json'

export default function SteelColumnForm({ onSubmit }) {
  const [sectionType, setSectionType] = useState('')
  const [sectionSize, setSectionSize] = useState('')
  const [steelGrade, setSteelGrade] = useState('')
  const [axialLoad, setAxialLoad] = useState('')
  const [length, setLength] = useState('')
  const [kFactor, setKFactor] = useState('1.0')
  const [boundary, setBoundary] = useState('Pinned-Pinned')

  const [availableSizes, setAvailableSizes] = useState([])
  const [dimensions, setDimensions] = useState({
    depth: '',
    width: '',
    flangeThickness: '',
    webThickness: ''
  })

  useEffect(() => {
    if (sectionType && sectionData[sectionType]) {
      setAvailableSizes(Object.keys(sectionData[sectionType]))
    } else {
      setAvailableSizes([])
    }
  }, [sectionType])

  useEffect(() => {
    if (sectionType && sectionSize && sectionData[sectionType]?.[sectionSize]) {
      const sec = sectionData[sectionType][sectionSize]
      setDimensions({
        depth: sec.h || '',
        width: sec.b || '',
        flangeThickness: sec.tf || '',
        webThickness: sec.tw || ''
      })
    }
  }, [sectionSize, sectionType])

  const handleSubmit = (e) => {
    e.preventDefault()
    const data = {
      sectionType,
      sectionSize,
      dimensions,
      steelGrade: parseFloat(steelGrade),
      axialLoad: parseFloat(axialLoad),
      length: parseFloat(length),
      kFactor: parseFloat(kFactor),
      boundaryCondition: boundary
    }
    onSubmit(data)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block font-medium mb-1">Section Type</label>
        <select value={sectionType} onChange={(e) => setSectionType(e.target.value)} className="input">
          <option value="">-- Select Type --</option>
          {Object.keys(sectionData).map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      {availableSizes.length > 0 && (
        <div>
          <label className="block font-medium mb-1">Section Size</label>
          <select value={sectionSize} onChange={(e) => setSectionSize(e.target.value)} className="input">
            <option value="">-- Select Size --</option>
            {availableSizes.map(size => (
              <option key={size} value={size}>{size}</option>
            ))}
          </select>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block font-medium mb-1">Depth h <span className="text-gray-500 text-sm">(mm)</span></label>
          <input type="number" value={dimensions.depth} readOnly className="input bg-gray-100" />
        </div>
        <div>
          <label className="block font-medium mb-1">Width b <span className="text-gray-500 text-sm">(mm)</span></label>
          <input type="number" value={dimensions.width} readOnly className="input bg-gray-100" />
        </div>
        <div>
          <label className="block font-medium mb-1">Flange Thickness tf <span className="text-gray-500 text-sm">(mm)</span></label>
          <input type="number" value={dimensions.flangeThickness} readOnly className="input bg-gray-100" />
        </div>
        <div>
          <label className="block font-medium mb-1">Web Thickness tw <span className="text-gray-500 text-sm">(mm)</span></label>
          <input type="number" value={dimensions.webThickness} readOnly className="input bg-gray-100" />
        </div>
      </div>

      <div>
        <label className="block font-medium mb-1">Steel Grade fy <span className="text-gray-500 text-sm">(MPa)</span></label>
        <input type="number" value={steelGrade} onChange={(e) => setSteelGrade(e.target.value)} className="input" />
      </div>

      <div>
        <label className="block font-medium mb-1">Axial Load <span className="text-gray-500 text-sm">(kN)</span></label>
        <input type="number" value={axialLoad} onChange={(e) => setAxialLoad(e.target.value)} className="input" />
      </div>

      <div>
        <label className="block font-medium mb-1">Column Length <span className="text-gray-500 text-sm">(mm)</span></label>
        <input type="number" value={length} onChange={(e) => setLength(e.target.value)} className="input" />
      </div>

      <div>
        <label className="block font-medium mb-1">Boundary Condition</label>
        <select value={boundary} onChange={(e) => setBoundary(e.target.value)} className="input">
          <option value="Pinned-Pinned">Pinned-Pinned</option>
          <option value="Fixed-Fixed">Fixed-Fixed</option>
          <option value="Fixed-Free">Fixed-Free</option>
          <option value="Custom">Custom</option>
        </select>
      </div>

      <div>
        <label className="block font-medium mb-1">Effective Length Factor (K)</label>
        <input type="number" step="0.01" value={kFactor} onChange={(e) => setKFactor(e.target.value)} className="input" />
      </div>

      <button type="submit" className="w-full bg-blue-600 text-white p-3 rounded hover:bg-blue-700 font-semibold">
        Analyze Steel Column
      </button>
    </form>
  )
}
