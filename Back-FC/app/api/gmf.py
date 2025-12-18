from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja


router = APIRouter()


class GMFRecalcRequest(BaseModel):
    fecha: date
    cuenta_bancaria_id: int
    usuario_id: Optional[int] = 1
    compania_id: Optional[int] = 1


@router.post("/recalculate", status_code=status.HTTP_200_OK)
def recalculate_gmf(payload: GMFRecalcRequest, db: Session = Depends(get_db)):
    """Forzar recálculo y persistencia de GMF para una fecha/cuenta.
    Utiliza la configuración vigente (última activa en o antes de la fecha; si no, la última activa).
    Después de calcular GMF, recalcula SUB-TOTAL TESORERÍA para incluir el nuevo GMF.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔄 [API GMF] Recálculo solicitado: fecha={payload.fecha}, cuenta={payload.cuenta_bancaria_id}")
    
    service = DependenciasFlujoCajaService(db)
    result = service.recalcular_gmf(
        fecha=payload.fecha,
        cuenta_id=payload.cuenta_bancaria_id,
        usuario_id=payload.usuario_id,
        compania_id=payload.compania_id,
    )
    
    if not result:
        logger.warning(f"⚠️ [API GMF] No se pudo recalcular GMF")
        raise HTTPException(status_code=404, detail="No hay configuración GMF vigente o base de componentes para la fecha")
    
    logger.info(f"✅ [API GMF] Recálculo GMF exitoso: monto={result.get('monto_nuevo', 0)}")
    
    # 🔄 IMPORTANTE: Después de actualizar GMF, recalcular SUB-TOTAL TESORERÍA
    # para que incluya el nuevo valor de GMF
    logger.info(f"🔄 [API GMF] Recalculando SUB-TOTAL TESORERÍA para incluir nuevo GMF...")
    try:
        from app.schemas.transacciones_flujo_caja import AreaTransaccion as AreaTransaccionSchema
        dependencias_result = service.procesar_dependencias_avanzadas(
            fecha=payload.fecha,
            area=AreaTransaccionSchema.tesoreria,
            concepto_modificado_id=49,  # GMF fue modificado
            cuenta_id=payload.cuenta_bancaria_id,
            compania_id=payload.compania_id,
            usuario_id=payload.usuario_id
        )
        logger.info(f"✅ [API GMF] SUB-TOTAL TESORERÍA recalculado: {len(dependencias_result)} dependencias procesadas")
    except Exception as e:
        logger.error(f"⚠️ [API GMF] Error recalculando dependencias: {e}")
    
    db.commit()
    
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
