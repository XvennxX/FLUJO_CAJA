"""
API endpoints para gestión de transacciones de flujo de caja
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

from ..core.database import get_db
from ..models import TransaccionFlujoCaja
from ..schemas.flujo_caja import (
    TransaccionFlujoCajaCreate,
    TransaccionFlujoCajaUpdate, 
    TransaccionFlujoCajaResponse,
    FlujoCajaDiarioResponse,
    FlujoCajaResumenResponse,
    AreaTransaccionSchema,
    AreaConceptoSchema
)
from ..services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
from ..api.auth import get_current_user

router = APIRouter(prefix="/api/transacciones-flujo-caja", tags=["Transacciones Flujo de Caja"])

@router.post("/", response_model=TransaccionFlujoCajaResponse, status_code=status.HTTP_201_CREATED)
def crear_transaccion(
    transaccion_data: TransaccionFlujoCajaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear una nueva transacción de flujo de caja"""
    try:
        service = TransaccionFlujoCajaService(db)
        transaccion = service.crear_transaccion(transaccion_data, current_user.id)
        return transaccion
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.get("/fecha/{fecha}", response_model=List[TransaccionFlujoCajaResponse])
def obtener_transacciones_por_fecha(
    fecha: date,
    area: Optional[AreaTransaccionSchema] = Query(None, description="Filtrar por área"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener todas las transacciones de una fecha específica"""
    service = TransaccionFlujoCajaService(db)
    transacciones = service.obtener_transacciones_por_fecha(fecha, area)
    return transacciones

@router.get("/{transaccion_id}", response_model=TransaccionFlujoCajaResponse)
def obtener_transaccion(
    transaccion_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener una transacción específica por ID"""
    service = TransaccionFlujoCajaService(db)
    transaccion = service.obtener_transaccion_por_id(transaccion_id)
    
    if not transaccion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
    
    return transaccion

@router.put("/{transaccion_id}", response_model=TransaccionFlujoCajaResponse)
def actualizar_transaccion(
    transaccion_id: int,
    transaccion_data: TransaccionFlujoCajaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar una transacción existente"""
    try:
        service = TransaccionFlujoCajaService(db)
        transaccion = service.actualizar_transaccion(transaccion_id, transaccion_data, current_user.id)
        
        if not transaccion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
        
        return transaccion
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.delete("/{transaccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transaccion(
    transaccion_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar una transacción"""
    service = TransaccionFlujoCajaService(db)
    eliminado = service.eliminar_transaccion(transaccion_id, current_user.id)
    
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")

# ============================================
# ENDPOINTS PARA REPORTES Y DASHBOARDS
# ============================================

@router.get("/flujo-diario/{fecha}/{area}", response_model=FlujoCajaDiarioResponse)
def obtener_flujo_caja_diario(
    fecha: date,
    area: AreaConceptoSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener el flujo de caja completo de un día específico para un área"""
    service = TransaccionFlujoCajaService(db)
    flujo_diario = service.obtener_flujo_caja_diario(fecha, area)
    return flujo_diario

@router.get("/resumen-periodo/{fecha_inicio}/{fecha_fin}/{area}", response_model=FlujoCajaResumenResponse)
def obtener_resumen_periodo(
    fecha_inicio: date,
    fecha_fin: date,
    area: AreaConceptoSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener resumen del flujo de caja para un período específico"""
    if fecha_inicio > fecha_fin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha de inicio debe ser menor o igual a la fecha de fin")
    
    service = TransaccionFlujoCajaService(db)
    resumen = service.obtener_resumen_periodo(fecha_inicio, fecha_fin, area)
    return resumen

# ============================================
# ENDPOINTS ESPECÍFICOS PARA DASHBOARDS
# ============================================

@router.get("/dashboard/tesoreria/{fecha}", response_model=FlujoCajaDiarioResponse)
def obtener_dashboard_tesoreria(
    fecha: date,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener datos específicos para el dashboard de tesorería"""
    service = TransaccionFlujoCajaService(db)
    flujo_diario = service.obtener_flujo_caja_diario(fecha, AreaConceptoSchema.tesoreria)
    return flujo_diario

@router.get("/dashboard/pagaduria/{fecha}", response_model=FlujoCajaDiarioResponse)
def obtener_dashboard_pagaduria(
    fecha: date,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener datos específicos para el dashboard de pagaduría"""
    service = TransaccionFlujoCajaService(db)
    flujo_diario = service.obtener_flujo_caja_diario(fecha, AreaConceptoSchema.pagaduria)
    return flujo_diario

# ============================================
# ENDPOINTS PARA MANEJO MASIVO
# ============================================

@router.post("/importar-masivo")
def importar_transacciones_masivo(
    transacciones: List[TransaccionFlujoCajaCreate],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Importar múltiples transacciones de una vez"""
    service = TransaccionFlujoCajaService(db)
    resultados = {"exitosas": 0, "fallidas": 0, "errores": []}
    
    for i, transaccion_data in enumerate(transacciones):
        try:
            service.crear_transaccion(transaccion_data, current_user.id)
            resultados["exitosas"] += 1
        except Exception as e:
            resultados["fallidas"] += 1
            resultados["errores"].append({
                "indice": i,
                "transaccion": transaccion_data.dict(),
                "error": str(e)
            })
    
    return resultados

@router.delete("/eliminar-fecha/{fecha}")
def eliminar_transacciones_fecha(
    fecha: date,
    area: Optional[AreaTransaccionSchema] = Query(None, description="Área específica a eliminar"),
    confirmar: bool = Query(False, description="Confirmar eliminación"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar todas las transacciones de una fecha específica"""
    if not confirmar:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe confirmar la eliminación con el parámetro 'confirmar=true'")
    
    service = TransaccionFlujoCajaService(db)
    transacciones = service.obtener_transacciones_por_fecha(fecha, area)
    
    eliminadas = 0
    for transaccion in transacciones:
        if service.eliminar_transaccion(transaccion.id, current_user.id):
            eliminadas += 1
    
    return {"message": f"Se eliminaron {eliminadas} transacciones de la fecha {fecha}"}
