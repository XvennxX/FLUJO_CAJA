"""
API endpoints para gestión de conceptos de flujo de caja
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

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
        concepto = service.actualizar_concepto(concepto_id, concepto_data)
        
        if not concepto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concepto no encontrado")
        
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
    eliminado = service.eliminar_concepto(concepto_id)
    
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concepto no encontrado")

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
