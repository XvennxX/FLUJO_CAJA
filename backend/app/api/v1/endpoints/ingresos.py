from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.services.transaction_service import TransactionService
from app.services.audit_service import AuditService
from app.schemas.transaction import IngresoCreate, IngresoResponse, IngresoUpdate

router = APIRouter()

@router.get("/", response_model=List[IngresoResponse])
async def listar_ingresos(
    skip: int = 0,
    limit: int = 100,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    id_cuenta: Optional[int] = None,
    id_concepto: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Listar ingresos con filtros opcionales"""
    
    # Crear servicios
    audit_service = AuditService(db)
    transaction_service = TransactionService(db, audit_service)
    
    try:
        # TODO: Obtener usuario actual del token
        user_id = 1  # Temporal
        
        ingresos = transaction_service.listar_ingresos(
            skip=skip,
            limit=limit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_cuenta=id_cuenta,
            id_concepto=id_concepto
        )
        
        return ingresos
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar ingresos: {str(e)}"
        )

@router.post("/", response_model=IngresoResponse)
async def crear_ingreso(
    ingreso_data: IngresoCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo ingreso"""
    
    # Crear servicios
    audit_service = AuditService(db)
    transaction_service = TransactionService(db, audit_service)
    
    try:
        # TODO: Obtener usuario actual del token
        user_id = 1  # Temporal
        
        nuevo_ingreso = transaction_service.crear_ingreso(
            ingreso_data=ingreso_data,
            user_id=user_id
        )
        
        return nuevo_ingreso
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear ingreso: {str(e)}"
        )

@router.get("/{ingreso_id}", response_model=IngresoResponse)
async def obtener_ingreso(
    ingreso_id: int,
    db: Session = Depends(get_db)
):
    """Obtener ingreso por ID"""
    
    # Crear servicios
    audit_service = AuditService(db)
    transaction_service = TransactionService(db, audit_service)
    
    try:
        ingreso = transaction_service.obtener_ingreso(ingreso_id)
        
        if not ingreso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingreso no encontrado"
            )
        
        return ingreso
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ingreso: {str(e)}"
        )

@router.put("/{ingreso_id}", response_model=IngresoResponse)
async def actualizar_ingreso(
    ingreso_id: int,
    ingreso_data: IngresoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar ingreso"""
    
    # Crear servicios
    audit_service = AuditService(db)
    transaction_service = TransactionService(db, audit_service)
    
    try:
        # TODO: Obtener usuario actual del token
        user_id = 1  # Temporal
        
        ingreso_actualizado = transaction_service.actualizar_ingreso(
            ingreso_id=ingreso_id,
            ingreso_data=ingreso_data,
            user_id=user_id
        )
        
        return ingreso_actualizado
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar ingreso: {str(e)}"
        )

@router.delete("/{ingreso_id}")
async def eliminar_ingreso(
    ingreso_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar ingreso"""
    
    # Crear servicios
    audit_service = AuditService(db)
    transaction_service = TransactionService(db, audit_service)
    
    try:
        # TODO: Obtener usuario actual del token
        user_id = 1  # Temporal
        
        result = transaction_service.eliminar_ingreso(
            ingreso_id=ingreso_id,
            user_id=user_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar ingreso: {str(e)}"
        )
