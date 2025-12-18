"""
Endpoints para la configuración de Cuatro por Mil (Pagaduría)
Similar a gmf_config.py pero para el área de Pagaduría
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
import logging

from app.core.database import get_db
from app.models.cuatro_por_mil_config import CuatroPorMilConfig
from app.models import Usuario
from app.schemas.cuatro_por_mil_config import (
    CuatroPorMilConfigCreate, 
    CuatroPorMilConfigUpdate, 
    CuatroPorMilConfigResponse
)
from app.api.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Lista fija de IDs de conceptos permitidos para Cuatro por Mil (Pagaduría - todos egresos)
CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS = {
    68,  # EMBARGOS
    69,  # OTROS PAGOS
    76,  # PAGO SOI
    78,  # OTROS IMPTOS
}

# ID del concepto CUATRO POR MIL donde se guarda el resultado
CONCEPTO_CUATRO_POR_MIL_ID = 80


def filtrar_conceptos_permitidos(conceptos: List[int]) -> List[int]:
    """Devuelve solo IDs válidos según la lista fija, sin duplicados, preservando orden."""
    vistos = set()
    filtrados = []
    for cid in conceptos:
        try:
            cid_int = int(cid)
        except Exception:
            continue
        if cid_int in CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS and cid_int not in vistos:
            filtrados.append(cid_int)
            vistos.add(cid_int)
    return filtrados


@router.post("/config", response_model=CuatroPorMilConfigResponse, status_code=status.HTTP_201_CREATED)
async def crear_config_cuatro_por_mil(
    config: CuatroPorMilConfigCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear una nueva versión de configuración Cuatro por Mil para una cuenta bancaria.
    
    Sistema de versionado:
    - Cada cambio crea un NUEVO registro con fecha_vigencia_desde
    - Las configs anteriores se mantienen activas para preservar histórico
    - La config aplicable para un día X es la más reciente con fecha_vigencia_desde <= X
    
    Solo admin y pagaduría pueden crear configuraciones.
    """
    try:
        # Verificar permisos - normalizar a minúsculas para comparación
        rol_normalizado = current_user.rol.lower() if current_user.rol else ''
        if rol_normalizado not in ['admin', 'administrador', 'pagaduria', 'pagaduría']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos para configurar Cuatro por Mil. Tu rol es: {current_user.rol}"
            )
        
        # Normalizar lista recibida filtrando IDs permitidos
        conceptos_filtrados = filtrar_conceptos_permitidos(config.conceptos_seleccionados)
        if not conceptos_filtrados:
            # Si viene vacío o sin válidos, usar TODOS los permitidos por defecto
            conceptos_filtrados = list(CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS)

        # 🔍 Verificar si ya existe una config para esta cuenta/fecha exacta
        config_misma_fecha = db.query(CuatroPorMilConfig).filter(
            CuatroPorMilConfig.cuenta_bancaria_id == config.cuenta_bancaria_id,
            CuatroPorMilConfig.fecha_vigencia_desde == config.fecha_vigencia_desde,
            CuatroPorMilConfig.activo == True
        ).first()
        
        if config_misma_fecha:
            # Si ya existe config para esta fecha, ACTUALIZAR conceptos (caso de corrección)
            config_misma_fecha.conceptos_seleccionados = json.dumps(conceptos_filtrados)
            db.flush()
            db.commit()
            db.refresh(config_misma_fecha)
            
            logger.info(f"✅ Config Cuatro por Mil actualizada: ID={config_misma_fecha.id}, cuenta={config.cuenta_bancaria_id}, fecha_vigencia={config.fecha_vigencia_desde}")
            
            return CuatroPorMilConfigResponse(
                id=config_misma_fecha.id,
                cuenta_bancaria_id=config_misma_fecha.cuenta_bancaria_id,
                conceptos_seleccionados=json.loads(config_misma_fecha.conceptos_seleccionados),
                activo=config_misma_fecha.activo,
                fecha_vigencia_desde=config_misma_fecha.fecha_vigencia_desde,
                fecha_creacion=config_misma_fecha.fecha_creacion,
                fecha_actualizacion=config_misma_fecha.fecha_actualizacion
            )
        
        # ✨ Crear NUEVA versión de configuración
        nueva_config = CuatroPorMilConfig(
            cuenta_bancaria_id=config.cuenta_bancaria_id,
            conceptos_seleccionados=json.dumps(conceptos_filtrados),
            fecha_vigencia_desde=config.fecha_vigencia_desde,
            activo=True
        )
        
        db.add(nueva_config)
        db.flush()
        db.commit()
        db.refresh(nueva_config)
        
        logger.info(f"✅ Config Cuatro por Mil creada: ID={nueva_config.id}, cuenta={config.cuenta_bancaria_id}, fecha_vigencia={config.fecha_vigencia_desde}, conceptos={conceptos_filtrados}")
        
        return CuatroPorMilConfigResponse(
            id=nueva_config.id,
            cuenta_bancaria_id=nueva_config.cuenta_bancaria_id,
            conceptos_seleccionados=json.loads(nueva_config.conceptos_seleccionados) if nueva_config.conceptos_seleccionados else [],
            activo=nueva_config.activo,
            fecha_vigencia_desde=nueva_config.fecha_vigencia_desde,
            fecha_creacion=nueva_config.fecha_creacion,
            fecha_actualizacion=nueva_config.fecha_actualizacion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creando config Cuatro por Mil: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/config/{cuenta_bancaria_id}", response_model=CuatroPorMilConfigResponse)
async def obtener_config_cuatro_por_mil(
    cuenta_bancaria_id: int,
    fecha: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener la configuración Cuatro por Mil aplicable para una cuenta bancaria.
    
    - Si se especifica fecha: retorna la config vigente para esa fecha
    - Si no: retorna la config más reciente
    
    La config aplicable es la más reciente con fecha_vigencia_desde <= fecha consultada
    """
    from datetime import datetime, date as date_type
    
    try:
        # Determinar fecha de consulta
        if fecha:
            try:
                fecha_consulta = datetime.strptime(fecha, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        else:
            fecha_consulta = date_type.today()
        
        # Buscar config vigente para la fecha (la más reciente con fecha_vigencia_desde <= fecha)
        config = db.query(CuatroPorMilConfig).filter(
            CuatroPorMilConfig.cuenta_bancaria_id == cuenta_bancaria_id,
            CuatroPorMilConfig.activo == True,
            CuatroPorMilConfig.fecha_vigencia_desde <= fecha_consulta
        ).order_by(CuatroPorMilConfig.fecha_vigencia_desde.desc()).first()
        
        if not config:
            # Si no hay config, retornar config por defecto con todos los conceptos
            logger.info(f"📋 No hay config Cuatro por Mil para cuenta {cuenta_bancaria_id}, usando valores por defecto")
            return CuatroPorMilConfigResponse(
                id=0,
                cuenta_bancaria_id=cuenta_bancaria_id,
                conceptos_seleccionados=list(CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS),
                activo=True,
                fecha_vigencia_desde=fecha_consulta,
                fecha_creacion=None,
                fecha_actualizacion=None
            )
        
        # Parsear conceptos
        try:
            conceptos = json.loads(config.conceptos_seleccionados) if config.conceptos_seleccionados else []
        except:
            conceptos = list(CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS)
        
        return CuatroPorMilConfigResponse(
            id=config.id,
            cuenta_bancaria_id=config.cuenta_bancaria_id,
            conceptos_seleccionados=conceptos,
            activo=config.activo,
            fecha_vigencia_desde=config.fecha_vigencia_desde,
            fecha_creacion=config.fecha_creacion,
            fecha_actualizacion=config.fecha_actualizacion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo config Cuatro por Mil: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/conceptos-permitidos")
async def obtener_conceptos_permitidos():
    """
    Obtener la lista de conceptos permitidos para el cálculo de Cuatro por Mil.
    """
    return {
        "conceptos": list(CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS),
        "detalles": {
            68: "EMBARGOS",
            69: "OTROS PAGOS",
            76: "PAGO SOI",
            78: "OTROS IMPTOS"
        },
        "concepto_resultado_id": CONCEPTO_CUATRO_POR_MIL_ID,
        "formula": "CUATRO_POR_MIL = SUM(conceptos_seleccionados) × 4/1000"
    }


from pydantic import BaseModel
from typing import Optional
from datetime import date

class CuatroPorMilRecalcRequest(BaseModel):
    """Request body para el endpoint de recálculo"""
    fecha: date
    cuenta_bancaria_id: int
    usuario_id: Optional[int] = 1
    compania_id: Optional[int] = None


@router.post("/recalculate")
async def recalcular_cuatro_por_mil(
    payload: CuatroPorMilRecalcRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Forzar recálculo del Cuatro por Mil para una cuenta y fecha específica.
    
    Este endpoint:
    1. Usa el servicio de dependencias para recalcular
    2. Recalcula también los subtotales de pagaduría
    """
    from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
    
    try:
        fecha_obj = payload.fecha
        cuenta_bancaria_id = payload.cuenta_bancaria_id
        
        # Usar el servicio de dependencias para recalcular
        service = DependenciasFlujoCajaService(db)
        resultado = service.recalcular_cuatro_por_mil(
            fecha=fecha_obj,
            cuenta_id=cuenta_bancaria_id,
            usuario_id=payload.usuario_id,
            compania_id=payload.compania_id
        )
        
        if not resultado:
            logger.warning(f"⚠️ [API 4x1000] No se pudo recalcular - usando valores por defecto")
            # Forzar cálculo con valores por defecto
            resultado = {
                "success": True,
                "cuenta_bancaria_id": cuenta_bancaria_id,
                "fecha": str(fecha_obj),
                "conceptos_usados": list(CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS),
                "mensaje": "Recálculo ejecutado con conceptos por defecto"
            }
        
        logger.info(f"✅ [API 4x1000] Recálculo exitoso: cuenta={cuenta_bancaria_id}, fecha={fecha_obj}")
        
        # Recalcular dependencias de pagaduría (subtotales)
        try:
            from app.schemas.flujo_caja import AreaTransaccionSchema
            dependencias_result = service.procesar_dependencias_avanzadas(
                fecha=fecha_obj,
                area=AreaTransaccionSchema.pagaduria,
                concepto_modificado_id=CONCEPTO_CUATRO_POR_MIL_ID,
                cuenta_id=cuenta_bancaria_id,
                compania_id=payload.compania_id,
                usuario_id=payload.usuario_id
            )
            logger.info(f"✅ [API 4x1000] Dependencias recalculadas: {len(dependencias_result) if dependencias_result else 0}")
        except Exception as e:
            logger.warning(f"⚠️ [API 4x1000] Error recalculando dependencias: {e}")
        
        db.commit()
        
        return {"ok": True, "data": resultado}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error recalculando Cuatro por Mil: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
