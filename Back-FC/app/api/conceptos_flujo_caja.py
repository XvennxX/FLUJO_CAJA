"""
API endpoints para gestión de conceptos de flujo de caja
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from ..core.database import get_db
from ..models import ConceptoFlujoCaja
from ..schemas.flujo_caja import (
    ConceptoFlujoCajaCreate,
    ConceptoFlujoCajaUpdate, 
    ConceptoFlujoCajaResponse,
    AreaConceptoSchema
)
from ..services.concepto_flujo_caja_service import ConceptoFlujoCajaService
from ..api.auth import get_current_user
from ..services.auditoria_service import AuditoriaService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/conceptos-flujo-caja", tags=["Conceptos Flujo de Caja"])

@router.post("/", response_model=ConceptoFlujoCajaResponse, status_code=status.HTTP_201_CREATED)
def crear_concepto(
    concepto_data: ConceptoFlujoCajaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear un nuevo concepto de flujo de caja"""
    try:
        service = ConceptoFlujoCajaService(db)
        concepto = service.crear_concepto(concepto_data)
        
        # 📝 AUDITORÍA: Registrar creación de concepto
        try:
            AuditoriaService.registrar_accion(
                db=db,
                usuario=current_user,
                accion="CREATE",
                modulo="CONCEPTOS",
                entidad="ConceptoFlujoCaja",
                entidad_id=str(concepto.id),
                descripcion=f"Creó nuevo concepto: {concepto.nombre} ({concepto.area.value})",
                valores_nuevos={
                    "nombre": concepto.nombre,
                    "codigo": concepto.codigo,
                    "area": concepto.area.value if hasattr(concepto.area, 'value') else str(concepto.area)
                }
            )
            logger.info(f"✅ Auditoría registrada: CREATE concepto {concepto.id}")
        except Exception as e:
            logger.warning(f"Error en auditoría de creación de concepto: {e}")
        
        return concepto
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.get("/", response_model=List[ConceptoFlujoCajaResponse])
def obtener_conceptos(
    area: Optional[AreaConceptoSchema] = Query(None, description="Filtrar por área"),
    activos_only: bool = Query(True, description="Solo conceptos activos"),
    busqueda: Optional[str] = Query(None, description="Buscar por nombre o código"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener lista de conceptos de flujo de caja"""
    service = ConceptoFlujoCajaService(db)
    
    if busqueda:
        conceptos = service.buscar_conceptos(busqueda, area)
    elif area:
        conceptos = service.obtener_conceptos_por_area(area, activos_only)
    else:
        # Obtener todos los conceptos
        conceptos = service.obtener_conceptos_por_area(AreaConceptoSchema.ambas, activos_only)
    
    return conceptos

@router.get("/por-area/{area}", response_model=List[ConceptoFlujoCajaResponse])
def obtener_conceptos_por_area(
    area: AreaConceptoSchema,
    activos_only: bool = Query(True, description="Solo conceptos activos"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener conceptos específicos de un área"""
    service = ConceptoFlujoCajaService(db)
    conceptos = service.obtener_conceptos_por_area(area, activos_only)
    return conceptos

@router.get("/{concepto_id}", response_model=ConceptoFlujoCajaResponse)
def obtener_concepto(
    concepto_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener un concepto específico por ID"""
    service = ConceptoFlujoCajaService(db)
    concepto = service.obtener_concepto_por_id(concepto_id)
    
    if not concepto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concepto no encontrado")
    
    return concepto

@router.put("/{concepto_id}", response_model=ConceptoFlujoCajaResponse)
def actualizar_concepto(
    concepto_id: int,
    concepto_data: ConceptoFlujoCajaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar un concepto existente"""
    try:
        service = ConceptoFlujoCajaService(db)
        
        # Obtener concepto anterior para auditoría
        concepto_anterior = service.obtener_concepto_por_id(concepto_id)
        if not concepto_anterior:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concepto no encontrado")
        
        valores_anteriores = {
            "nombre": concepto_anterior.nombre,
            "codigo": concepto_anterior.codigo,
            "area": concepto_anterior.area.value if hasattr(concepto_anterior.area, 'value') else str(concepto_anterior.area),
            "activo": concepto_anterior.activo
        }
        
        concepto = service.actualizar_concepto(concepto_id, concepto_data)
        
        if not concepto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concepto no encontrado")
        
        # 📝 AUDITORÍA: Registrar actualización de concepto
        try:
            valores_nuevos = {
                "nombre": concepto.nombre,
                "codigo": concepto.codigo,
                "area": concepto.area.value if hasattr(concepto.area, 'value') else str(concepto.area),
                "activo": concepto.activo
            }
            
            AuditoriaService.registrar_accion(
                db=db,
                usuario=current_user,
                accion="UPDATE",
                modulo="CONCEPTOS",
                entidad="ConceptoFlujoCaja",
                entidad_id=str(concepto.id),
                descripcion=f"Actualizó concepto: {concepto.nombre}",
                valores_anteriores=valores_anteriores,
                valores_nuevos=valores_nuevos
            )
            logger.info(f"✅ Auditoría registrada: UPDATE concepto {concepto.id}")
        except Exception as e:
            logger.warning(f"Error en auditoría de actualización de concepto: {e}")
        
        return concepto
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.delete("/{concepto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_concepto(
    concepto_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar un concepto (soft delete si tiene transacciones)"""
    service = ConceptoFlujoCajaService(db)
    
    # Obtener concepto antes de eliminar para auditoría
    concepto = service.obtener_concepto_por_id(concepto_id)
    if not concepto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concepto no encontrado")
    
    nombre_concepto = concepto.nombre
    codigo_concepto = concepto.codigo
    area_concepto = concepto.area.value if hasattr(concepto.area, 'value') else str(concepto.area)
    
    eliminado = service.eliminar_concepto(concepto_id)
    
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concepto no encontrado")
    
    # 📝 AUDITORÍA: Registrar eliminación de concepto
    try:
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="DELETE",
            modulo="CONCEPTOS",
            entidad="ConceptoFlujoCaja",
            entidad_id=str(concepto_id),
            descripcion=f"Eliminó concepto: {nombre_concepto} ({area_concepto})",
            valores_anteriores={
                "nombre": nombre_concepto,
                "codigo": codigo_concepto,
                "area": area_concepto
            }
        )
        logger.info(f"✅ Auditoría registrada: DELETE concepto {concepto_id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de eliminación de concepto: {e}")

@router.get("/dependencias/{area}", response_model=List[ConceptoFlujoCajaResponse])
def obtener_conceptos_con_dependencias(
    area: AreaConceptoSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener conceptos que tienen dependencias configuradas"""
    service = ConceptoFlujoCajaService(db)
    conceptos = service.obtener_conceptos_con_dependencias(area)
    return conceptos

@router.post("/reordenar/{area}")
def reordenar_conceptos(
    area: AreaConceptoSchema,
    conceptos_ordenados: List[int],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Reordenar conceptos de un área específica"""
    service = ConceptoFlujoCajaService(db)
    resultado = service.reordenar_conceptos(area, conceptos_ordenados)
    
    if not resultado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al reordenar conceptos")
    
    return {"message": "Conceptos reordenados exitosamente"}

@router.get("/estadisticas/generales")
def obtener_estadisticas(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener estadísticas generales de conceptos"""
    service = ConceptoFlujoCajaService(db)
    estadisticas = service.obtener_estadisticas_conceptos()
    return estadisticas
