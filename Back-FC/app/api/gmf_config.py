"""
Endpoints para la configuración GMF
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.models import GMFConfig, Usuario
from app.schemas.gmf_config import GMFConfigCreate, GMFConfigUpdate, GMFConfigResponse
from app.api.auth import get_current_user

router = APIRouter()

# Lista fija de IDs de conceptos permitidos para GMF
CONCEPTOS_GMF_PERMITIDOS = {
    5,   # PAGOS INTERCOMPAÑÍAS
    9,   # APERTURA ACTIVO FINANCIERO
    12,  # CANCELACIÓN KW
    13,  # PAGO INTERESES KW
    29,  # EGRESO DIVIDENDOS
    34,  # FORWARD (E)
    35,  # FORWARD (I)
    43,  # EMBARGOS
    31,  # SWAP
    47,  # COMISIONES
    36,  # COMPRA DIVISAS OTRAS ÁREAS
    26,  # COMPRA ACCIONES
    22,  # LLAMADO CAPITAL FCP
    32,  # OPCIONES (E)
    33,  # OPCIONES (I)
    45,  # OTROS
    25,  # TRASLADO ARL
    46,  # IMPUESTOS
}

def filtrar_conceptos_permitidos(conceptos: List[int]) -> List[int]:
    """Devuelve solo IDs válidos según la lista fija, sin duplicados, preservando orden."""
    vistos = set()
    filtrados = []
    for cid in conceptos:
        try:
            cid_int = int(cid)
        except Exception:
            continue
        if cid_int in CONCEPTOS_GMF_PERMITIDOS and cid_int not in vistos:
            filtrados.append(cid_int)
            vistos.add(cid_int)
    return filtrados

@router.post("/", response_model=GMFConfigResponse, status_code=status.HTTP_201_CREATED)
async def crear_config_gmf(
    config: GMFConfigCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear una nueva versión de configuración GMF para una cuenta bancaria.
    
    Sistema de versionado:
    - Cada cambio crea un NUEVO registro con fecha_vigencia_desde
    - Las configs anteriores se mantienen activas para preservar histórico
    - La config aplicable para un día X es la más reciente con fecha_vigencia_desde <= X
    
    Solo admin y tesorería pueden crear configuraciones.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Verificar permisos - normalizar a minúsculas para comparación
        rol_normalizado = current_user.rol.lower() if current_user.rol else ''
        if rol_normalizado not in ['admin', 'administrador', 'tesoreria', 'tesorería']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos para configurar GMF. Tu rol es: {current_user.rol}"
            )
        
        # Normalizar lista recibida filtrando IDs permitidos
        conceptos_filtrados = filtrar_conceptos_permitidos(config.conceptos_seleccionados)
        if not conceptos_filtrados:
            # Si viene vacío o sin válidos, usar TODOS los permitidos por defecto
            conceptos_filtrados = list(CONCEPTOS_GMF_PERMITIDOS)

        # 🔍 Verificar si ya existe una config para esta cuenta/fecha exacta
        config_misma_fecha = db.query(GMFConfig).filter(
            GMFConfig.cuenta_bancaria_id == config.cuenta_bancaria_id,
            GMFConfig.fecha_vigencia_desde == config.fecha_vigencia_desde,
            GMFConfig.activo == True
        ).first()
        
        if config_misma_fecha:
            # Si ya existe config para esta fecha, ACTUALIZAR conceptos (caso de corrección)
            config_misma_fecha.conceptos_seleccionados = json.dumps(conceptos_filtrados)
            db.flush()  # Forzar escritura inmediata
            db.commit()
            db.refresh(config_misma_fecha)
            
            logger.info(f"✅ Config GMF actualizada: ID={config_misma_fecha.id}, cuenta={config.cuenta_bancaria_id}, fecha_vigencia={config.fecha_vigencia_desde}")
            
            # Parsear conceptos para respuesta ANTES de retornar
            response_data = GMFConfigResponse(
                id=config_misma_fecha.id,
                cuenta_bancaria_id=config_misma_fecha.cuenta_bancaria_id,
                conceptos_seleccionados=json.loads(config_misma_fecha.conceptos_seleccionados),
                activo=config_misma_fecha.activo,
                fecha_vigencia_desde=config_misma_fecha.fecha_vigencia_desde,
                fecha_creacion=config_misma_fecha.fecha_creacion,
                fecha_actualizacion=config_misma_fecha.fecha_actualizacion
            )
            return response_data
        
        # ✨ Crear NUEVA versión de configuración (no sobrescribir)
        nueva_config = GMFConfig(
            cuenta_bancaria_id=config.cuenta_bancaria_id,
            conceptos_seleccionados=json.dumps(conceptos_filtrados),
            fecha_vigencia_desde=config.fecha_vigencia_desde,
            activo=True
        )
        
        db.add(nueva_config)
        db.flush()  # Forzar escritura inmediata
        db.commit()
        db.refresh(nueva_config)
        
        logger.info(f"✅ Config GMF creada: ID={nueva_config.id}, cuenta={config.cuenta_bancaria_id}, fecha_vigencia={config.fecha_vigencia_desde}, conceptos={conceptos_filtrados}")
        
        # Parsear conceptos para respuesta ANTES de retornar
        response_data = GMFConfigResponse(
            id=nueva_config.id,
            cuenta_bancaria_id=nueva_config.cuenta_bancaria_id,
            conceptos_seleccionados=json.loads(nueva_config.conceptos_seleccionados) if nueva_config.conceptos_seleccionados else [],
            activo=nueva_config.activo,
            fecha_vigencia_desde=nueva_config.fecha_vigencia_desde,
            fecha_creacion=nueva_config.fecha_creacion,
            fecha_actualizacion=nueva_config.fecha_actualizacion
        )
        return response_data
        
    except HTTPException:
        # Re-lanzar excepciones HTTP sin modificar
        raise
    except Exception as e:
        logger.error(f"❌ Error creando config GMF: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/{cuenta_bancaria_id}", response_model=GMFConfigResponse)
async def obtener_config_gmf(
    cuenta_bancaria_id: int,
    fecha: str = None,  # Opcional: obtener config vigente para fecha específica (formato YYYY-MM-DD)
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener la configuración GMF vigente para una cuenta.
    Si se proporciona fecha, devuelve la config vigente para esa fecha.
    Si no, devuelve la más reciente.
    """
    from datetime import datetime
    
    query = db.query(GMFConfig).filter(
        GMFConfig.cuenta_bancaria_id == cuenta_bancaria_id,
        GMFConfig.activo == True
    )
    
    # Si se especifica fecha, filtrar por fecha_vigencia_desde <= fecha
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            query = query.filter(GMFConfig.fecha_vigencia_desde <= fecha_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    # Ordenar por fecha_vigencia_desde descendente (más reciente primero)
    config = query.order_by(GMFConfig.fecha_vigencia_desde.desc()).first()
    
    if not config:
        # Retornar configuración vacía en lugar de error
        from datetime import date as date_type
        return {
            "id": 0,
            "cuenta_bancaria_id": cuenta_bancaria_id,
            "conceptos_seleccionados": [],
            "activo": True,
            "fecha_vigencia_desde": fecha_obj if fecha else date_type.today(),
            "fecha_creacion": None,
            "fecha_actualizacion": None
        }
    
    # Parsear conceptos para respuesta
    config.conceptos_seleccionados = json.loads(config.conceptos_seleccionados) if config.conceptos_seleccionados else []
    return config

@router.put("/{cuenta_bancaria_id}", response_model=GMFConfigResponse)
async def actualizar_config_gmf(
    cuenta_bancaria_id: int,
    config_update: GMFConfigUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar la configuración GMF de una cuenta bancaria.
    Solo admin y tesorería pueden actualizar configuraciones.
    """
    # Verificar permisos - normalizar a minúsculas para comparación
    rol_normalizado = current_user.rol.lower() if current_user.rol else ''
    if rol_normalizado not in ['admin', 'administrador', 'tesoreria', 'tesorería']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tienes permisos para configurar GMF. Tu rol es: {current_user.rol}"
        )
    
    # Filtrar lista recibida
    conceptos_filtrados = filtrar_conceptos_permitidos(config_update.conceptos_seleccionados)
    if not conceptos_filtrados:
        conceptos_filtrados = list(CONCEPTOS_GMF_PERMITIDOS)

    config = db.query(GMFConfig).filter(
        GMFConfig.cuenta_bancaria_id == cuenta_bancaria_id,
        GMFConfig.activo == True
    ).first()
    
    if not config:
        # Crear nueva configuración si no existe
        nueva_config = GMFConfig(
            cuenta_bancaria_id=cuenta_bancaria_id,
            conceptos_seleccionados=json.dumps(conceptos_filtrados),
            activo=config_update.activo
        )
        db.add(nueva_config)
        db.commit()
        db.refresh(nueva_config)
        
        # Parsear conceptos para respuesta
        nueva_config.conceptos_seleccionados = json.loads(nueva_config.conceptos_seleccionados) if nueva_config.conceptos_seleccionados else []
        return nueva_config
    
    # Actualizar configuración existente
    config.conceptos_seleccionados = json.dumps(conceptos_filtrados)
    config.activo = config_update.activo
    
    db.commit()
    db.refresh(config)
    
    # Parsear conceptos para respuesta
    config.conceptos_seleccionados = json.loads(config.conceptos_seleccionados) if config.conceptos_seleccionados else []
    return config

@router.delete("/{cuenta_bancaria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_config_gmf(
    cuenta_bancaria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Desactivar la configuración GMF de una cuenta bancaria.
    Solo admin y tesorería pueden eliminar configuraciones.
    """
    # Verificar permisos - normalizar a minúsculas para comparación
    rol_normalizado = current_user.rol.lower() if current_user.rol else ''
    if rol_normalizado not in ['admin', 'administrador', 'tesoreria', 'tesorería']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tienes permisos para configurar GMF. Tu rol es: {current_user.rol}"
        )
    
    config = db.query(GMFConfig).filter(
        GMFConfig.cuenta_bancaria_id == cuenta_bancaria_id,
        GMFConfig.activo == True
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración GMF no encontrada"
        )
    
    # Desactivar en lugar de eliminar
    config.activo = False
    db.commit()
    
    return None

@router.get("/", response_model=List[GMFConfigResponse])
async def listar_configs_gmf(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Listar todas las configuraciones GMF activas.
    """
    configs = db.query(GMFConfig).filter(
        GMFConfig.activo == True
    ).offset(skip).limit(limit).all()
    
    # Parsear conceptos para cada configuración
    for config in configs:
        config.conceptos_seleccionados = json.loads(config.conceptos_seleccionados) if config.conceptos_seleccionados else []
    
    return configs
