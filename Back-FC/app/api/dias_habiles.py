"""
API endpoints para gestión de días hábiles.
Proporciona endpoints para determinar días laborables en Colombia.
"""
from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.dias_habiles_service import DiasHabilesService
from app.models.dias_festivos import DiaFestivo

router = APIRouter()


def get_dias_habiles_service(db: Session = Depends(get_db)) -> DiasHabilesService:
    """Dependency para obtener el servicio de días hábiles."""
    return DiasHabilesService(db)


@router.get("/validar/{fecha}")
async def validar_dia_habil(
    fecha: date,
    service: DiasHabilesService = Depends(get_dias_habiles_service)
):
    """
    Validar si una fecha específica es día hábil.
    
    Args:
        fecha: Fecha a validar (formato YYYY-MM-DD)
        
    Returns:
        Información sobre si es día hábil y detalles adicionales
    """
    try:
        info = service.obtener_info_dia(fecha)
        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al validar fecha: {str(e)}")


@router.get("/proximo/{fecha}")
async def obtener_proximo_dia_habil(
    fecha: date,
    incluir_actual: bool = Query(False, description="Incluir la fecha actual si es hábil"),
    service: DiasHabilesService = Depends(get_dias_habiles_service)
):
    """
    Obtener el próximo día hábil desde una fecha.
    
    Args:
        fecha: Fecha de referencia
        incluir_actual: Si incluir la fecha actual en la búsqueda
        
    Returns:
        Próximo día hábil
    """
    try:
        proximo = service.proximo_dia_habil(fecha, incluir_actual)
        return {
            "success": True,
            "data": {
                "fecha_referencia": fecha.isoformat(),
                "proximo_dia_habil": proximo.isoformat(),
                "incluyo_actual": incluir_actual and fecha == proximo
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener próximo día hábil: {str(e)}")


@router.get("/anterior/{fecha}")
async def obtener_anterior_dia_habil(
    fecha: date,
    incluir_actual: bool = Query(False, description="Incluir la fecha actual si es hábil"),
    service: DiasHabilesService = Depends(get_dias_habiles_service)
):
    """
    Obtener el día hábil anterior a una fecha.
    
    Args:
        fecha: Fecha de referencia
        incluir_actual: Si incluir la fecha actual en la búsqueda
        
    Returns:
        Día hábil anterior
    """
    try:
        anterior = service.anterior_dia_habil(fecha, incluir_actual)
        return {
            "success": True,
            "data": {
                "fecha_referencia": fecha.isoformat(),
                "anterior_dia_habil": anterior.isoformat(),
                "incluyo_actual": incluir_actual and fecha == anterior
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener día hábil anterior: {str(e)}")


@router.get("/rango")
async def obtener_dias_habiles_rango(
    fecha_inicio: date = Query(..., description="Fecha de inicio del rango"),
    fecha_fin: date = Query(..., description="Fecha de fin del rango"),
    solo_contar: bool = Query(False, description="Solo retornar el conteo"),
    service: DiasHabilesService = Depends(get_dias_habiles_service)
):
    """
    Obtener días hábiles en un rango de fechas.
    
    Args:
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin
        solo_contar: Si solo retornar el conteo de días
        
    Returns:
        Lista de días hábiles o conteo según parámetro
    """
    try:
        if fecha_inicio > fecha_fin:
            raise HTTPException(
                status_code=400, 
                detail="La fecha de inicio debe ser menor o igual a la fecha de fin"
            )
        
        if solo_contar:
            conteo = service.contar_dias_habiles_rango(fecha_inicio, fecha_fin)
            return {
                "success": True,
                "data": {
                    "fecha_inicio": fecha_inicio.isoformat(),
                    "fecha_fin": fecha_fin.isoformat(),
                    "total_dias_habiles": conteo
                }
            }
        else:
            dias_habiles = service.obtener_dias_habiles_rango(fecha_inicio, fecha_fin)
            return {
                "success": True,
                "data": {
                    "fecha_inicio": fecha_inicio.isoformat(),
                    "fecha_fin": fecha_fin.isoformat(),
                    "dias_habiles": [dia.isoformat() for dia in dias_habiles],
                    "total": len(dias_habiles)
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener rango de días hábiles: {str(e)}")


@router.get("/mes/{anio}/{mes}")
async def obtener_dias_habiles_mes(
    anio: int,
    mes: int,
    service: DiasHabilesService = Depends(get_dias_habiles_service)
):
    """
    Obtener información de días hábiles de un mes específico.
    
    Args:
        año: Año del mes
        mes: Mes (1-12)
        
    Returns:
        Información completa del mes incluyendo primer y último día hábil
    """
    try:
        if mes < 1 or mes > 12:
            raise HTTPException(status_code=400, detail="El mes debe estar entre 1 y 12")
        
        if anio < 2020 or anio > 2030:
            raise HTTPException(status_code=400, detail="El año debe estar entre 2020 y 2030")
        
        primer_dia = service.obtener_primer_dia_habil_mes(anio, mes)
        ultimo_dia = service.obtener_ultimo_dia_habil_mes(anio, mes)
        
        # Obtener todos los días hábiles del mes
        fecha_inicio = date(anio, mes, 1)
        if mes == 12:
            fecha_fin = date(anio + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin = date(anio, mes + 1, 1) - timedelta(days=1)
        
        dias_habiles = service.obtener_dias_habiles_rango(fecha_inicio, fecha_fin)
        
        return {
            "success": True,
            "data": {
                "año": anio,
                "mes": mes,
                "primer_dia_habil": primer_dia.isoformat(),
                "ultimo_dia_habil": ultimo_dia.isoformat(),
                "total_dias_habiles": len(dias_habiles),
                "dias_habiles": [dia.isoformat() for dia in dias_habiles]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener días hábiles del mes: {str(e)}")


@router.get("/hoy")
async def obtener_info_hoy(
    service: DiasHabilesService = Depends(get_dias_habiles_service)
):
    """
    Obtener información sobre el día actual y próximo día hábil.
    
    Returns:
        Información del día actual y próximo día hábil
    """
    try:
        hoy = date.today()
        info_hoy = service.obtener_info_dia(hoy)
        
        # Usar el próximo día hábil que ya está en info_hoy
        proximo_habil = info_hoy["proximo_habil"]
        
        return {
            "success": True,
            "data": {
                "hoy": info_hoy,
                "proximo_dia_habil": proximo_habil,
                "es_hoy_habil": info_hoy["es_habil"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener información de hoy: {str(e)}")


@router.get("/festivos")
async def obtener_festivos(
    anio: Optional[int] = Query(None, description="Año específico"),
    mes: Optional[int] = Query(None, description="Mes específico (requiere año)"),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de días festivos.
    
    Args:
        año: Año específico (opcional)
        mes: Mes específico (opcional, requiere año)
        
    Returns:
        Lista de días festivos
    """
    try:
        query = db.query(DiaFestivo).filter(DiaFestivo.activo == True)
        
        if anio:
            if mes:
                if mes < 1 or mes > 12:
                    raise HTTPException(status_code=400, detail="El mes debe estar entre 1 y 12")
                # Filtrar por año y mes específico
                fecha_inicio = date(anio, mes, 1)
                if mes == 12:
                    fecha_fin = date(anio + 1, 1, 1) - timedelta(days=1)
                else:
                    fecha_fin = date(anio, mes + 1, 1) - timedelta(days=1)
                query = query.filter(
                    DiaFestivo.fecha >= fecha_inicio,
                    DiaFestivo.fecha <= fecha_fin
                )
            else:
                # Filtrar solo por año
                fecha_inicio = date(anio, 1, 1)
                fecha_fin = date(anio, 12, 31)
                query = query.filter(
                    DiaFestivo.fecha >= fecha_inicio,
                    DiaFestivo.fecha <= fecha_fin
                )
        
        festivos = query.order_by(DiaFestivo.fecha).all()
        
        return {
            "success": True,
            "data": {
                "festivos": [festivo.to_dict() for festivo in festivos],
                "total": len(festivos),
                "filtros": {
                    "año": anio,
                    "mes": mes
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener festivos: {str(e)}")


# Importar timedelta para el endpoint de mes
from datetime import timedelta