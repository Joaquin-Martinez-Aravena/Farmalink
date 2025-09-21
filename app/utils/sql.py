
# app/utils/sql.py

from typing import Any, Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DBAPIError
from fastapi import HTTPException

async def run_select(db: AsyncSession, sql: str, **params) -> List[Dict[str, Any]]:
    rs = await db.execute(text(sql), params)
    return [dict(r) for r in rs.mappings().all()]

async def run_exec(db: AsyncSession, sql: str, **params) -> Dict[str, Any]:
    try:
        await db.execute(text(sql), params)
        await db.commit()
        return {"ok": True}
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"IntegrityError: {str(e.orig)}")
    except DBAPIError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"DBAPIError: {str(e.orig)}")

async def run_scalar(db: AsyncSession, sql: str, **params) -> Optional[Any]:
    rs = await db.execute(text(sql), params)
    row = rs.first()
    return row[0] if row else None

