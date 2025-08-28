from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from .structure_analyzer import StructureAnalyzer
from .code_router import get_code_handler
from .load_combination import generate_combinations   # ⬅️ جديد

router = APIRouter()

# ================================
# Pydantic Models (نفس JSON القادم من الفرونت)
# ================================
class Node(BaseModel):
    id: str
    x: float
    y: float
    support: str = "free"  # pin, fix, roller, free

class Member(BaseModel):
    id: str
    n1: str
    n2: str
    type: str = "beam"  # beam, column
    sectionId: str
    materialId: str
    loads: Optional[List[Dict]] = []

class Slab(BaseModel):
    id: str
    x: float
    y: float
    w: float
    h: float
    t: float
    materialId: str

class Material(BaseModel):
    id: str
    name: str
    fc: float
    fy: float
    E: float

class Section(BaseModel):
    id: str
    name: str
    shape: str
    params: Dict

class LoadCombination(BaseModel):
    id: str
    name: str
    expr: str

class StructureModel(BaseModel):
    code: str
    units: Dict
    materials: List[Material]
    sections: List[Section]
    nodes: List[Node]
    members: List[Member]
    slabs: List[Slab]
    loads: Dict


# ================================
# Endpoint
# ================================
@router.post("/structure/analyze")
def analyze_structure(structure: StructureModel):
    try:
        code = structure.code.upper()
        handler = get_code_handler(code)

        if not handler:
            raise HTTPException(status_code=400, detail=f"Unsupported code: {code}")

        # ⬇️ توليد load combinations حسب الكود
        structure_dict = structure.dict()
        structure_dict["loads"]["combinations"] = generate_combinations(code)

        # ⬇️ استدعاء StructureAnalyzer
        analyzer = StructureAnalyzer(structure_dict)
        raw_results = analyzer.analyze_combinations()

        # ⬇️ تمرير النتائج للهاندلر (checks لكل combo)
        results = {}
        for combo_id, combo_result in raw_results.items():
            results[combo_id] = handler.analyze_structure(structure_dict, combo_result)

        return {
            "status": "success",
            "code": code,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
