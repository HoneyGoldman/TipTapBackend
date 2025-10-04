from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, select
from app.core.deps import get_db, OptionalAuth
from app.models.report import ReportConfiguration
from app.schemas.report import ReportRunRequest
import json
import logging

router = APIRouter(prefix="/reports", tags=["reports"])
logger = logging.getLogger(__name__)

@router.post("/run")
def run_report(body: ReportRunRequest, db: Session = Depends(get_db), user=Depends(OptionalAuth)):
    report_name = body.report_name
    params = body.parameters

    cfg = db.execute(
        select(ReportConfiguration).where(ReportConfiguration.report_name == report_name, ReportConfiguration.is_active == 1)
    ).scalar_one_or_none()
    if not cfg:
        raise HTTPException(status_code=404, detail="Report not found")

    # Enforce authorization requirement per report
    try:
        needs_auth = int(getattr(cfg, "authorized_required", 1)) == 1
    except Exception:
        needs_auth = True
    if needs_auth and not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # parameters is stored as a JSON column; in most drivers this is returned as a Python object
    # Support both cases (string vs already-parsed list)
    if isinstance(cfg.parameters, str):
        schema = json.loads(cfg.parameters)
    else:
        schema = cfg.parameters
    # Validate params, apply defaults
    call_args = []
    for p in schema:
        name = p["parameter_name"]
        mandatory = bool(p.get("is_mandatory"))
        expects_user_id = name in ("p_user_id", "p_manager_user_id", "p_requester_id")
        if name in params:
            val = params[name]
            # Auto-fill user id params from auth context if invalid type was sent
            if expects_user_id:
                if isinstance(val, (dict, list)) and user:
                    val = user.id
                elif isinstance(val, str):
                    try:
                        val = int(val)
                    except Exception:
                        if user:
                            val = user.id
                        else:
                            raise HTTPException(status_code=400, detail=f"Invalid value for {name}")
            # Serialize complex structures to JSON strings for MySQL procedures
            if isinstance(val, (dict, list)):
                try:
                    val = json.dumps(val)
                except Exception:
                    pass
            call_args.append(val)
        elif not mandatory:
            val = p.get("default_value")
            if expects_user_id and (val is None) and user:
                val = user.id
            if isinstance(val, (dict, list)):
                try:
                    val = json.dumps(val)
                except Exception:
                    pass
            call_args.append(val)
        else:
            # Allow implicit default for user id params from auth context
            if expects_user_id and user:
                call_args.append(user.id)
            else:
                raise HTTPException(status_code=400, detail=f"Missing parameter: {name}")

    # Build CALL statement with named binds to satisfy SQLAlchemy 2.x param handling
    bind_names = [f"p{i}" for i in range(len(call_args))]
    placeholders = ",".join([f":{bn}" for bn in bind_names])
    sql = text(f"CALL {cfg.procedure_name}({placeholders})")
    bind_params = {bn: call_args[i] for i, bn in enumerate(bind_names)}

    # Debug logs (avoid logging secrets in production)
    try:
        logger.debug("reports.run report=%s procedure=%s", report_name, cfg.procedure_name)
        logger.debug("reports.run schema=%s", schema)
        logger.debug("reports.run sql=%s", f"CALL {cfg.procedure_name}({placeholders})")
        logger.debug("reports.run bind_keys=%s", list(bind_params.keys()))
    except Exception:
        pass

    try:
        res = db.execute(sql, bind_params)
        rows = [dict(r._mapping) for r in res]
        # Persist any DML performed inside procedures
        db.commit()
    except Exception:
        db.rollback()
        raise
    # Some MySQL drivers require fetching next result sets for CALL; keep simple here.
    return {"report_name": report_name, "rows": rows}
