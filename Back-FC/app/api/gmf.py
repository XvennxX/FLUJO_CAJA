from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja


router = APIRouter(prefix="/gmf", tags=["GMF"])


class GMFRecalcRequest(BaseModel):
    fecha: date
    cuenta_bancaria_id: int
    usuario_id: Optional[int] = 1
    compania_id: Optional[int] = 1


@router.post("/recalculate", status_code=status.HTTP_200_OK)
def recalculate_gmf(payload: GMFRecalcRequest, db: Session = Depends(get_db)):
    """Forzar recálculo y persistencia de GMF para una fecha/cuenta.
    Utiliza la configuración vigente (última activa en o antes de la fecha; si no, la última activa).
    """
    service = DependenciasFlujoCajaService(db)
    result = service.recalcular_gmf(
        fecha=payload.fecha,
        cuenta_id=payload.cuenta_bancaria_id,
        usuario_id=payload.usuario_id,
        compania_id=payload.compania_id,
    )
    db.commit()
    if not result:
        raise HTTPException(status_code=404, detail="No hay configuración GMF vigente o base de componentes para la fecha")
    return {"ok": True, "data": result}


@router.get("/value")
def get_gmf_value(fecha: date, cuenta_bancaria_id: int, db: Session = Depends(get_db)):
    """Obtener el valor GMF persistido en tesorería para una fecha/cuenta."""
    concepto_gmf = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.nombre == "GMF").first()
    if not concepto_gmf:
        raise HTTPException(status_code=404, detail="Concepto GMF no existe")

    trans = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha,
        TransaccionFlujoCaja.concepto_id == concepto_gmf.id,
        TransaccionFlujoCaja.cuenta_id == cuenta_bancaria_id,
        TransaccionFlujoCaja.area == AreaTransaccion.tesoreria,
    ).first()

    if not trans:
        return {"ok": True, "data": None}

    return {
        "ok": True,
        "data": {
            "fecha": fecha.isoformat(),
            "cuenta_id": cuenta_bancaria_id,
            "monto": float(trans.monto),
            "auditoria": trans.auditoria,
        },
    }
