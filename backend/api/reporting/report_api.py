"""Read-only v1 trace and PDF endpoints for server-owned analysis runs."""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from .models import AnalysisRunRecord, REPORT_SCHEMA_VERSION
from .pdf import render_report_bytes
from .run_store import RUN_STORE


logger = logging.getLogger(__name__)
router = APIRouter(tags=["v1 traceable reports"])


def _run_or_404(run_id: str) -> AnalysisRunRecord:
    record = RUN_STORE.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Analysis run was not found")
    return record


@router.get("/api/v1/analysis-runs/{run_id}", response_model=AnalysisRunRecord)
def get_analysis_run(run_id: str) -> AnalysisRunRecord:
    return _run_or_404(run_id)


@router.get("/api/v1/reports/{run_id}.pdf")
def get_report(run_id: str) -> Response:
    record = _run_or_404(run_id)
    try:
        content = render_report_bytes(record)
    except Exception:
        logger.exception("Traceable report generation failed for run %s", run_id)
        raise HTTPException(status_code=500, detail="Report generation could not be completed")
    return Response(
        content=content, media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="structicode-{record.run_id}.pdf"',
            "X-Analysis-Run-Id": record.run_id,
            "X-Report-Schema-Version": REPORT_SCHEMA_VERSION,
        },
    )
