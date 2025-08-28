import React, { useState, useRef } from "react";
import { motion } from "framer-motion";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "";

// الأكواد المدعومة (متوافقة مع أسماء الـ backend)
const codes = [
  { id: "ACI", name: "ACI 318-19 (USA)" },
  { id: "AS", name: "AS 3600/4100 (Australia)" },
  { id: "BS", name: "BS 8110/5950 (UK)" },
  { id: "CSA", name: "CSA A23.3 / S16 (Canada)" },
  { id: "Eurocode", name: "Eurocode 2 & 3 (Europe)" },
  { id: "Jordan", name: "Jordanian Code" },
  { id: "Turkey", name: "Turkish Code" },
  { id: "UAE", name: "UAE Code" },
  { id: "Saudi", name: "Saudi Code" },
  { id: "Egypt", name: "Egyptian Code" },
  { id: "IS", name: "Indian Standards" },
];

export default function StructureDesigner() {
  const svgRef = useRef(null);

  const [nodes, setNodes] = useState([]);
  const [members, setMembers] = useState([]);
  const [slabs, setSlabs] = useState([]);

  const [selectedCode, setSelectedCode] = useState("ACI");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [activeCombo, setActiveCombo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [drawingMember, setDrawingMember] = useState(null);
  const [lastPayload, setLastPayload] = useState(null);

  // إضافة Node بالضغط على الكانفس
  const handleCanvasClick = (e) => {
    const rect = svgRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 20; // scale to 20m viewbox
    const y = ((e.clientY - rect.top) / rect.height) * 10; // scale to 10m viewbox
    const id = `N${nodes.length + 1}`;
    setNodes([...nodes, { id, x: parseFloat(x.toFixed(2)), y: parseFloat(y.toFixed(2)), support: "free" }]);
  };

  // بدء/إنهاء رسم Member
  const handleNodeClick = (nid) => {
    if (!drawingMember) {
      setDrawingMember(nid);
    } else {
      if (nid !== drawingMember) {
        const id = `M${members.length + 1}`;
        setMembers([
          ...members,
          { id, n1: drawingMember, n2: nid, type: "beam", sectionId: "300x600", materialId: "C25_FY420", loads: [] },
        ]);
      }
      setDrawingMember(null);
    }
  };

  // إضافة Slab تجريبية (مستطيل ثابت)
  const addSlab = () => {
    const id = `S${slabs.length + 1}`;
    setSlabs([...slabs, { id, x: 5, y: 5, w: 4, h: 2, t: 0.2, materialId: "C25_FY420" }]);
  };

  // ================================
  // API Call
  // ================================
  const analyzeStructure = async () => {
    try {
      setLoading(true);
      setError(null);

      const payload = {
        code: selectedCode,
        units: { length: "m", force: "kN" },
        materials: [{ id: "C25_FY420", name: "RC fc=25, fy=420", fc: 25, fy: 420, E: 25000 }],
        sections: [{ id: "300x600", name: "Rect 300x600", shape: "rectRC", params: { bw: 0.3, h: 0.6, cover: 0.04 } }],
        nodes,
        members,
        slabs,
        loads: { combinations: [] },
      };

      const res = await axios.post(`${API_BASE}/structure/analyze`, payload, {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
      });

      setLastPayload(payload);
      setAnalysisResult(res.data.results);
      setActiveCombo(Object.keys(res.data.results)[0] || null); // أول Combination بشكل افتراضي
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // ================================
  // PDF Export
  // ================================
  const downloadPDF = async () => {
    if (!lastPayload || !analysisResult) return;
    try {
      const res = await fetch(`${API_BASE}/generate-pdf`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ data: lastPayload, result: analysisResult }),
      });

      if (!res.ok) throw new Error("Failed to generate PDF");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "structure_report.pdf";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("PDF Download Error:", err);
    }
  };

  return (
    <div className="w-full h-[92vh] grid grid-cols-12 gap-4 p-4 bg-gray-50">
      {/* Left Panel */}
      <div className="col-span-4 flex flex-col gap-3">
        <motion.div layout className="bg-white rounded-2xl shadow p-4">
          <h2 className="text-xl font-semibold mb-3">Settings</h2>
          <label className="block text-sm mb-2">
            Select Code:
            <select
              className="w-full mt-1 border rounded-lg p-2"
              value={selectedCode}
              onChange={(e) => setSelectedCode(e.target.value)}
            >
              {codes.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </label>
          <button onClick={addSlab} className="mt-3 px-3 py-1 bg-blue-400 text-white rounded-lg w-full">
            Add Slab
          </button>
        </motion.div>

        <motion.div layout className="bg-white rounded-2xl shadow p-4">
          <button
            onClick={analyzeStructure}
            className="w-full px-4 py-2 rounded-xl bg-green-600 text-white hover:bg-green-700"
          >
            {loading ? "Analyzing..." : "Analyze Structure"}
          </button>
          {error && <p className="text-red-600 mt-2">{error}</p>}
        </motion.div>

        {analysisResult && (
          <motion.div layout className="bg-white rounded-2xl shadow p-4 overflow-auto max-h-[50vh]">
            <h2 className="text-xl font-semibold mb-2">Results</h2>

            {/* تبويبات لكل Combination */}
            <div className="flex gap-2 mb-3 flex-wrap">
              {Object.keys(analysisResult).map((combo) => (
                <button
                  key={combo}
                  onClick={() => setActiveCombo(combo)}
                  className={`px-3 py-1 rounded-lg border ${
                    activeCombo === combo ? "bg-blue-600 text-white" : "bg-gray-100"
                  }`}
                >
                  {combo}
                </button>
              ))}
            </div>

            {activeCombo && (
              <div>
                <h3 className="font-semibold mb-2">Load Combination: {activeCombo}</h3>

                {/* Displacements */}
                <h4 className="font-medium mt-3">Displacements</h4>
                <table className="w-full text-xs border mt-1 mb-2">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="border p-1">Node</th>
                      <th className="border p-1">ux</th>
                      <th className="border p-1">uy</th>
                      <th className="border p-1">rz</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(analysisResult[activeCombo].displacements || {}).map(([nid, disp]) => (
                      <tr key={nid}>
                        <td className="border p-1">{nid}</td>
                        <td className="border p-1">{disp.ux.toFixed(4)}</td>
                        <td className="border p-1">{disp.uy.toFixed(4)}</td>
                        <td className="border p-1">{disp.rz.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Member Forces */}
                <h4 className="font-medium mt-3">Member Forces</h4>
                <table className="w-full text-xs border mt-1 mb-2">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="border p-1">Member</th>
                      <th className="border p-1">Nmax</th>
                      <th className="border p-1">Vmax</th>
                      <th className="border p-1">Mmax</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(analysisResult[activeCombo].member_forces || {}).map(([mid, f]) => (
                      <tr key={mid}>
                        <td className="border p-1">{mid}</td>
                        <td className="border p-1">{f.Nmax.toFixed(2)}</td>
                        <td className="border p-1">{f.Vmax.toFixed(2)}</td>
                        <td className="border p-1">{f.Mmax.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Design Checks */}
                <h4 className="font-medium mt-3">Design Checks</h4>
                <table className="w-full text-xs border mt-1">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="border p-1">Member</th>
                      <th className="border p-1">Mu</th>
                      <th className="border p-1">Vu</th>
                      <th className="border p-1">Nu</th>
                      <th className="border p-1">As_req</th>
                      <th className="border p-1">OK</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(analysisResult[activeCombo].design || {}).map(([mid, d]) => (
                      <tr key={mid}>
                        <td className="border p-1">{mid}</td>
                        <td className="border p-1">{d.Mu?.toFixed(2)}</td>
                        <td className="border p-1">{d.Vu?.toFixed(2)}</td>
                        <td className="border p-1">{d.Nu?.toFixed(2)}</td>
                        <td className="border p-1">{d.As_required}</td>
                        <td className="border p-1">{d.Overall_OK ? "✅" : "❌"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* زر PDF */}
                <div className="text-center mt-4">
                  <button
                    onClick={downloadPDF}
                    className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700"
                  >
                    Download PDF Report
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Right Panel (Sketch Canvas) */}
      <div className="col-span-8 bg-white rounded-2xl shadow relative overflow-hidden">
        <svg ref={svgRef} viewBox="0 0 20 10" width="100%" height="100%" onClick={handleCanvasClick}>
          {/* Slabs */}
          {slabs.map((s) => (
            <rect
              key={s.id}
              x={s.x}
              y={s.y - s.h}
              width={s.w}
              height={s.h}
              fill="lightblue"
              stroke="blue"
              strokeWidth={0.05}
            />
          ))}

          {/* Members */}
          {members.map((m) => {
            const n1 = nodes.find((n) => n.id === m.n1);
            const n2 = nodes.find((n) => n.id === m.n2);
            return (
              <line key={m.id} x1={n1.x} y1={n1.y} x2={n2.x} y2={n2.y} stroke="blue" strokeWidth={0.05} />
            );
          })}

          {/* Nodes */}
          {nodes.map((n) => (
            <circle
              key={n.id}
              cx={n.x}
              cy={n.y}
              r={0.2}
              fill={drawingMember === n.id ? "red" : "black"}
              onClick={(e) => {
                e.stopPropagation();
                handleNodeClick(n.id);
              }}
            />
          ))}
        </svg>
      </div>
    </div>
  );
}
