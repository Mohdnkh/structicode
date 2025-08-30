from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

# ✅ استيراد صحيح لمسار utils
from backend.api.utils.pdf_generator import generate_pdf
from backend.engine import structure_router
from backend.engine.load_combination import combine_loads
from backend.engine.code_router import get_code_handler
from backend.engine.seismic_router import get_seismic_handler
from backend.engine.concrete.slab_solid import analyze_solid_slab
from backend.engine.concrete.slab_hollow import analyze_hollow_slab
from backend.engine.concrete.slab_waffle import analyze_waffle_slab
from backend.engine.concrete.beam import analyze_concrete_beam
from backend.engine.concrete.column import analyze_concrete_column
from backend.engine.concrete.footing import analyze_concrete_footing
from backend.engine.concrete.staircase import analyze_concrete_staircase

app = FastAPI()

app.include_router(structure_router.router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisInput(BaseModel):
    code: str
    element: str
    data: dict
    seismic: dict | None = None

class PDFRequest(BaseModel):
    data: dict
    result: dict

@app.post("/analyze")
async def analyze_element(payload: AnalysisInput):
    code = payload.code
    element_type = payload.element
    seismic_data = payload.seismic

    if element_type == "slab" and "geometry" in payload.data:
        geom = payload.data.pop("geometry")
        data = {**payload.data, **geom}
    else:
        data = payload.data

    try:
        if element_type == "slab":
            slab_type = data.get("type", "solid")
            if slab_type == "solid":
                structural = analyze_solid_slab(data)
            elif slab_type == "hollow":
                structural = analyze_hollow_slab(data)
            elif slab_type == "waffle":
                structural = analyze_waffle_slab(data)
            else:
                return {"status": "error", "message": f"Unsupported slab type: {slab_type}"}
        elif element_type == "beam":
            structural = analyze_concrete_beam(data, code)
        elif element_type == "column":
            structural = analyze_concrete_column(data, code)
        elif element_type == "footing":
            structural = analyze_concrete_footing(data, code)
        elif element_type == "staircase":
            structural = analyze_concrete_staircase(data)
        else:
            handler = get_code_handler(code)
            if not handler:
                return {"status": "error", "message": "Unsupported code"}
            structural = handler.analyze(element_type, data)

        seismic_result = None
        if seismic_data:
            seismic_handler = get_seismic_handler(code)
            if seismic_handler:
                seismic_result = seismic_handler.analyze(seismic_data)

        return {
            "status": "success",
            "element": element_type,
            "result": {
                "structural": structural,
                "seismic": seismic_result
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/generate-pdf")
async def generate_pdf_report(request: PDFRequest):
    try:
        filename = "report.pdf"
        path = generate_pdf(request.data, request.result, filename)
        if not os.path.exists(path):
            raise HTTPException(status_code=500, detail="PDF not generated")
        return FileResponse(path, media_type="application/pdf", filename=filename)
    except Exception as e:
        print("PDF generation failed:", e)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {e}")

# ✅ لخدمة ملفات React بعد الـ build
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    index_path = os.path.join("frontend", "dist", "index.html")
    return FileResponse(index_path)
