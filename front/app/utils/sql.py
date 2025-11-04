# app/utils/sql.py

from typing import Any, Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, DBAPIError
from fastapi import HTTPException
from sqlalchemy.orm import Session  # Cambiar de AsyncSession a Session

def run_select(db: Session, sql: str, **params) -> List[Dict[str, Any]]:
    rs = db.execute(text(sql), params)  # Eliminar await
    return [dict(r) for r in rs.mappings().all()]

def run_exec(db: Session, sql: str, **params) -> Dict[str, Any]:
    try:
        db.execute(text(sql), params)  # Eliminar await
        db.commit()  # Commit sincrónico
        return {"ok": True}
    except IntegrityError as e:
        db.rollback()  # Rollback sincrónico
        raise HTTPException(status_code=409, detail=f"IntegrityError: {str(e.orig)}")
    except DBAPIError as e:
        db.rollback()  # Rollback sincrónico
        raise HTTPException(status_code=400, detail=f"DBAPIError: {str(e.orig)}")

def run_scalar(db: Session, sql: str, **params) -> Optional[Any]:
    rs = db.execute(text(sql), params)  # Eliminar await
    row = rs.first()
    return row[0] if row else None
