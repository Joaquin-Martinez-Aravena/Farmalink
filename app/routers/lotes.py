from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..bd import get_db  # Aquí cambiamos get_session por get_db
from ..models import Lote, AjusteLote
from ..schemas.lote import AjusteIn

r = APIRouter(prefix="/api/lotes", tags=["Lotes"])

@r.get("/")
def listar(db: Session = Depends(get_db)):  
    res = db.query(Lote).order_by(Lote.fecha_venc.asc()).all()
    return res

@r.post("/{id_lote}/ajustes")
def ajustar(id_lote: int, data: AjusteIn, db: Session = Depends(get_db)):  
    lot = db.get(Lote, id_lote)
    if not lot:
        raise HTTPException(404, "Lote no encontrado")
    
    nuevo = lot.stock_lote + data.delta
    if nuevo < 0:
        raise HTTPException(400, "El stock no puede quedar negativo")

    db.add(AjusteLote(id_lote=id_lote, delta=data.delta, motivo=data.motivo, id_usuario=data.id_usuario))
    lot.stock_lote = nuevo
    db.commit()
    db.refresh(lot)
    return {"ok": True, "stock_lote": lot.stock_lote}
