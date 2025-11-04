"""
API endpoints para conciliación contable
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from decimal import Decimal

from ..core.database import get_db
from ..api.auth import get_current_user
from ..services.auditoria_service import AuditoriaService
from ..services.conciliacion_contable_service import ConciliacionContableService
from ..schemas.conciliacion_contable import (
    ConciliacionFechaRequest,
    ConciliacionFechaResponse,
    EmpresaConciliacionResponse
)
from ..models.usuarios import Usuario
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/conciliacion", tags=["conciliacion"])

@router.post("/fecha", response_model=ConciliacionFechaResponse)
async def obtener_conciliacion_por_fecha(
    fecha_request: ConciliacionFechaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener datos de conciliación para una fecha específica
    """
    try:
        logger.info(f"🔍 Obteniendo conciliación para fecha: {fecha_request.fecha}")
        conciliacion_data = ConciliacionContableService.obtener_conciliacion_por_fecha(
            db=db,
            fecha=fecha_request.fecha
        )
        logger.info(f"✅ Conciliación obtenida: {len(conciliacion_data.empresas)} empresas")
        
        # 📝 AUDITORÍA: Registrar consulta de conciliación
        try:
            AuditoriaService.registrar_accion(
                db=db,
                usuario=current_user,
                accion="READ",
                modulo="CONCILIACION",
                entidad="ConciliacionContable",
                descripcion=f"Consultó conciliación para fecha: {fecha_request.fecha}",
                valores_nuevos={"fecha": str(fecha_request.fecha)}
            )
        except Exception as audit_error:
            logger.warning(f"Error en auditoría de consulta conciliación: {audit_error}")
        
        return conciliacion_data
        
    except Exception as e:
        import traceback
        logger.error(f"❌ Error obteniendo conciliación para fecha {fecha_request.fecha}: {e}")
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo conciliación: {str(e)}"
        )

@router.put("/centralizadora/{empresa_id}")
async def actualizar_total_centralizadora(
    empresa_id: int,
    fecha: date,
    total_centralizadora: Decimal,
    observaciones: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar el total centralizadora de una empresa para una fecha específica
    """
    try:
        conciliacion = ConciliacionContableService.actualizar_total_centralizadora(
            db=db,
            empresa_id=empresa_id,
            fecha=fecha,
            total_centralizadora=total_centralizadora,
            observaciones=observaciones
        )
        
        # 📝 AUDITORÍA: Registrar actualización de total centralizadora
        try:
            AuditoriaService.registrar_accion(
                db=db,
                usuario=current_user,
                accion="UPDATE",
                modulo="CONCILIACION",
                entidad="ConciliacionContable",
                entidad_id=str(conciliacion.id),
                descripcion=f"Actualizó total centralizadora: ${total_centralizadora:,.2f} para empresa {empresa_id}",
                valores_nuevos={
                    "empresa_id": empresa_id,
                    "fecha": str(fecha),
                    "total_centralizadora": str(total_centralizadora)
                }
            )
        except Exception as audit_error:
            logger.warning(f"Error en auditoría de actualización centralizadora: {audit_error}")
        
        return {
            "message": "Total centralizadora actualizado exitosamente",
            "conciliacion_id": conciliacion.id,
            "diferencia": conciliacion.diferencia_calculada,
            "estado": conciliacion.estado_conciliacion
        }
        
    except Exception as e:
        logger.error(f"Error actualizando total centralizadora: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando total centralizadora: {str(e)}"
        )

@router.put("/evaluar/{empresa_id}")
async def evaluar_conciliacion(
    empresa_id: int,
    fecha: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Evaluar una conciliación específica (cambiar estado de Pendiente a Evaluado)
    """
    try:
        conciliacion = ConciliacionContableService.evaluar_conciliacion(
            db=db,
            empresa_id=empresa_id,
            fecha=fecha
        )
        
        # 📝 AUDITORÍA: Registrar evaluación de conciliación
        try:
            AuditoriaService.registrar_accion(
                db=db,
                usuario=current_user,
                accion="UPDATE",
                modulo="CONCILIACION",
                entidad="ConciliacionContable",
                entidad_id=str(conciliacion.id),
                descripcion=f"Evaluó conciliación para empresa {empresa_id} en fecha {fecha}",
                valores_nuevos={
                    "empresa_id": empresa_id,
                    "fecha": str(fecha),
                    "estado": "Evaluado"
                }
            )
        except Exception as audit_error:
            logger.warning(f"Error en auditoría de evaluación conciliación: {audit_error}")
        
        return {
            "message": "Conciliación evaluada exitosamente",
            "conciliacion_id": conciliacion.id,
            "estado": conciliacion.estado
        }
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error evaluando conciliación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluando conciliación: {str(e)}"
        )

@router.put("/confirmar/{empresa_id}")
async def confirmar_conciliacion(
    empresa_id: int,
    fecha: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Confirmar una conciliación específica (cambiar estado de Evaluado a Confirmado)
    """
    try:
        conciliacion = ConciliacionContableService.confirmar_conciliacion(
            db=db,
            empresa_id=empresa_id,
            fecha=fecha
        )
        
        # 📝 AUDITORÍA: Registrar confirmación de conciliación
        try:
            AuditoriaService.registrar_accion(
                db=db,
                usuario=current_user,
                accion="UPDATE",
                modulo="CONCILIACION",
                entidad="ConciliacionContable",
                entidad_id=str(conciliacion.id),
                descripcion=f"Confirmó conciliación para empresa {empresa_id} en fecha {fecha}",
                valores_nuevos={
                    "empresa_id": empresa_id,
                    "fecha": str(fecha),
                    "estado": "Confirmado"
                }
            )
        except Exception as audit_error:
            logger.warning(f"Error en auditoría de confirmación conciliación: {audit_error}")
        
        return {
            "message": "Conciliación confirmada exitosamente",
            "conciliacion_id": conciliacion.id,
            "estado": conciliacion.estado
        }
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error confirmando conciliación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error confirmando conciliación: {str(e)}"
        )

@router.put("/cerrar/{empresa_id}")
async def cerrar_conciliacion(
    empresa_id: int,
    fecha: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cerrar una conciliación específica (cambiar estado de Confirmado a Cerrado)
    """
    try:
        conciliacion = ConciliacionContableService.cerrar_conciliacion(
            db=db,
            empresa_id=empresa_id,
            fecha=fecha
        )
        
        # 📝 AUDITORÍA: Registrar cierre de conciliación
        try:
            AuditoriaService.registrar_accion(
                db=db,
                usuario=current_user,
                accion="UPDATE",
                modulo="CONCILIACION",
                entidad="ConciliacionContable",
                entidad_id=str(conciliacion.id),
                descripcion=f"Cerró conciliación para empresa {empresa_id} en fecha {fecha}",
                valores_nuevos={
                    "empresa_id": empresa_id,
                    "fecha": str(fecha),
                    "estado": "Cerrado"
                }
            )
        except Exception as audit_error:
            logger.warning(f"Error en auditoría de cierre conciliación: {audit_error}")
        
        return {
            "message": "Conciliación cerrada exitosamente",
            "conciliacion_id": conciliacion.id,
            "estado": conciliacion.estado
        }
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error cerrando conciliación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cerrando conciliación: {str(e)}"
        )

@router.put("/evaluar-todas")
async def evaluar_todas_conciliaciones(
    fecha: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Evaluar todas las conciliaciones de una fecha
    """
    try:
        conciliaciones = ConciliacionContableService.evaluar_todas_conciliaciones(
            db=db,
            fecha=fecha
        )
        
        # 📝 AUDITORÍA: Registrar evaluación masiva
        try:
            AuditoriaService.registrar_accion(
                db=db,
                usuario=current_user,
                accion="UPDATE",
                modulo="CONCILIACION",
                entidad="ConciliacionContable",
                descripcion=f"Evaluó todas las conciliaciones para fecha {fecha}",
                valores_nuevos={
                    "fecha": str(fecha),
                    "total_conciliaciones": len(conciliaciones)
                }
            )
        except Exception as audit_error:
            logger.warning(f"Error en auditoría de evaluación masiva: {audit_error}")
        
        return {
            "message": f"Se evaluaron {len(conciliaciones)} conciliaciones",
            "fecha": fecha,
            "total_evaluadas": len(conciliaciones)
        }
        
    except Exception as e:
        logger.error(f"Error evaluando conciliaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluando conciliaciones: {str(e)}"
        )

@router.put("/cerrar-todas")
async def cerrar_todas_conciliaciones(
    fecha: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cerrar todas las conciliaciones de una fecha (las marca como confirmadas)
    """
    try:
        # Primero evaluar todas
        conciliaciones = ConciliacionContableService.evaluar_todas_conciliaciones(
            db=db,
            fecha=fecha
        )
        
        # Luego confirmar cada una
        confirmadas = 0
        for conciliacion in conciliaciones:
            if conciliacion.total_centralizadora is not None:
                ConciliacionContableService.confirmar_conciliacion(
                    db=db,
                    empresa_id=conciliacion.empresa_id,
                    fecha=fecha
                )
                confirmadas += 1
        
        # 📝 AUDITORÍA: Registrar cierre masivo
        try:
            AuditoriaService.registrar_accion(
                db=db,
                usuario=current_user,
                accion="UPDATE",
                modulo="CONCILIACION",
                entidad="ConciliacionContable",
                descripcion=f"Cerró todas las conciliaciones para fecha {fecha}",
                valores_nuevos={
                    "fecha": str(fecha),
                    "total_confirmadas": confirmadas
                }
            )
        except Exception as audit_error:
            logger.warning(f"Error en auditoría de cierre masivo: {audit_error}")
        
        return {
            "message": f"Se cerraron {confirmadas} conciliaciones",
            "fecha": fecha,
            "total_cerradas": confirmadas
        }
        
    except Exception as e:
        logger.error(f"Error cerrando conciliaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cerrando conciliaciones: {str(e)}"
        )