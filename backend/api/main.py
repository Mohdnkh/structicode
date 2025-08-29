from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os



from .engine.load_combination import combine_loads
from .engine.code_router import get_code_handler
from .engine.seismic_router import get_seismic_handler
from .utils.pdf_generator import generate_pdf

from .engine.concrete.slab_solid import analyze_solid_slab
from .engine.concrete.slab_hollow import analyze_hollow_slab
from .engine.concrete.slab_waffle import analyze_waffle_slab

from .engine.concrete.beam import analyze_concrete_beam
from .engine.concrete.column import analyze_concrete_column
from .engine.concrete.footing import analyze_concrete_footing
from .engine.concrete.staircase import analyze_concrete_staircase

# ⬇️ استيراد الروتر الجديد
from .engine import structure_router

app = FastAPI()



# ✅ ربط الراوترات
 
app.include_router(structure_router.router, prefix="/api")

# ✅ إعداد CORS
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

# ✅ حماية التحليل باستخدام JWT
@app.post("/analyze")

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
            "code": handler.get_code_info() if 'handler' in locals() and hasattr(handler, "get_code_info") else {},
            "element": element_type,
            "result": {
                "structural": structural,
                "seismic": seismic_result
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/generate-pdf")

        filename = "report.pdf"
        combined_data = {
            **request.data,
            "code": request.data.get("code"),
            "element": request.data.get("element")
        }
        path = generate_pdf(combined_data, request.result, filename)
        return FileResponse(path, media_type='application/pdf', filename=filename)
    except Exception as e:
        print("PDF generation failed:", e)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {e}")



# ✅ خدمة ملفات React (frontend/dist)
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# ✅ fallback لأي route → يرجّع index.html
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    index_path = os.path.join("frontend", "dist", "index.html")
    return FileResponse(index_path)
