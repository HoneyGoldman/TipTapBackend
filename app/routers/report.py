from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, select
from app.core.deps import get_db, AuthUser
from app.models.report import ReportConfiguration
from app.schemas.report import ReportRunRequest
import json

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/run", dependencies=[Depends(AuthUser)])
def run_report(body: ReportRunRequest, db: Session = Depends(get_db)):
    report_name = body.report_name
    params = body.parameters

    cfg = db.execute(
        select(ReportConfiguration).where(ReportConfiguration.report_name == report_name, ReportConfiguration.is_active == 1)
    ).scalar_one_or_none()
    if not cfg:
        raise HTTPException(status_code=404, detail="Report not found")

    schema = json.loads(cfg.parameters)
    # Validate params, apply defaults
    call_args = []
    for p in schema:
        name = p["parameter_name"]
        mandatory = bool(p.get("is_mandatory"))
        if name in params:
            call_args.append(params[name])
        elif not mandatory:
            call_args.append(p.get("default_value"))
        else:
            raise HTTPException(status_code=400, detail=f"Missing parameter: {name}")

    # Build CALL statement with placeholders
    placeholders = ",".join(["%s"] * len(call_args))
    sql = text(f"CALL {cfg.procedure_name}({placeholders})")

    res = db.execute(sql, tuple(call_args))
    rows = [dict(r._mapping) for r in res]
    # Some MySQL drivers require fetching next result sets for CALL; keep simple here.
    return {"report_name": report_name, "rows": rows}
