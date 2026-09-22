"""Read-only v1 trace and PDF endpoints for P7 ephemeral and P9 project runs."""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from .models import AnalysisRunRecord, REPORT_SCHEMA_VERSION
from .pdf import render_report_bytes
from .run_store import RUN_STORE
from ..auth.security import EnterpriseError, current_user_from_request
from ..data.database import session_scope
from ..data.models import PersistentAnalysisRun
from ..data.services import load_persistent_run, report_record
router=APIRouter(tags=["v1 traceable reports"])

def _persistent_row(run_id:str):
    try:
        with session_scope() as session:
            row=session.get(PersistentAnalysisRun,run_id)
            return row
    except Exception as exc:
        raise EnterpriseError("PERSISTENCE_ERROR","Local data storage is unavailable",503) from exc

def _run_for_request(run_id:str,request:Request)->tuple[AnalysisRunRecord,tuple|None]:
    # Protected database rows always win over the anonymous in-memory store.
    if _persistent_row(run_id) is not None:
        user=current_user_from_request(request)
        try:
            with session_scope() as session:
                row,record=load_persistent_run(session,user.id,run_id)
                return record,(row.project_id,user.id)
        except EnterpriseError: raise
        except Exception as exc: raise EnterpriseError("PERSISTENCE_ERROR","Local data storage is unavailable",503) from exc
    record=RUN_STORE.get(run_id)
    if record is None: raise HTTPException(status_code=404,detail="Analysis run was not found")
    return record,None
@router.get("/api/v1/analysis-runs/{run_id}",response_model=AnalysisRunRecord)
def get_analysis_run(run_id:str,request:Request,response:Response)->AnalysisRunRecord:
    response.headers["Cache-Control"]="no-store"
    return _run_for_request(run_id,request)[0]
@router.get("/api/v1/reports/{run_id}.pdf")
def get_report(run_id:str,request:Request)->Response:
    record,ownership=_run_for_request(run_id,request)
    try: content=render_report_bytes(record)
    except Exception as exc: raise HTTPException(status_code=500,detail="Report generation could not be completed") from exc
    if ownership is not None:
        project_id,user_id=ownership
        try:
            with session_scope() as session:
                row,_=load_persistent_run(session,user_id,run_id);report_record(session,row,user_id,content,REPORT_SCHEMA_VERSION)
        except EnterpriseError: raise
        except Exception as exc: raise EnterpriseError("PERSISTENCE_ERROR","Report generation could not be recorded",503) from exc
    return Response(content=content,media_type="application/pdf",headers={"Cache-Control":"no-store","Content-Disposition":f'attachment; filename="structicode-{record.run_id}.pdf"',"X-Analysis-Run-Id":record.run_id,"X-Report-Schema-Version":REPORT_SCHEMA_VERSION})
