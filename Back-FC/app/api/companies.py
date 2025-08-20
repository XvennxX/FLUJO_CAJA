from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..models.companias import Compania
from ..models.bancos import Banco
from ..schemas.companies import (
    CompaniaCreate, 
    CompaniaUpdate, 
    CompaniaResponse, 
    CompaniaListResponse
)
from ..api.auth import get_current_user

router = APIRouter(prefix="/companies", tags=["companies"])

# Endpoint temporal para testing sin autenticación
@router.get("/test", response_model=List[CompaniaListResponse])
async def get_companies_test(
    db: Session = Depends(get_db)
):
    """
    Endpoint temporal para probar sin autenticación - todas las compañías
    """
    companies = db.query(Compania).all()
    return companies

# Endpoint temporal para crear sin autenticación
@router.post("/test", response_model=CompaniaResponse, status_code=status.HTTP_201_CREATED)
async def create_company_test(
    company_data: CompaniaCreate,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva compañía sin autenticación (temporal)
    """
    # Verificar si ya existe una compañía con el mismo nombre
    existing_company = db.query(Compania).filter(
        Compania.nombre.ilike(company_data.nombre)
    ).first()
    
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una compañía con ese nombre"
        )
    
    # Crear nueva compañía
    new_company = Compania(
        nombre=company_data.nombre
    )
    
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    
    return new_company

# Endpoint temporal para actualizar sin autenticación
@router.put("/test/{company_id}", response_model=CompaniaResponse)
async def update_company_test(
    company_id: int,
    company_data: CompaniaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar una compañía sin autenticación (temporal)
    """
    company = db.query(Compania).filter(Compania.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compañía no encontrada"
        )
    
    # Verificar duplicados si se cambia el nombre
    if company_data.nombre and company_data.nombre != company.nombre:
        existing_company = db.query(Compania).filter(
            Compania.nombre.ilike(company_data.nombre),
            Compania.id != company_id
        ).first()
        
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una compañía con ese nombre"
            )
    
    # Actualizar campos
    if company_data.nombre is not None:
        company.nombre = company_data.nombre
    
    db.commit()
    db.refresh(company)
    
    return company

# Endpoint temporal para eliminar sin autenticación
@router.delete("/test/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_test(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar una compañía sin autenticación (temporal)
    """
    company = db.query(Compania).filter(Compania.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compañía no encontrada"
        )
    
    # Verificar si tiene cuentas bancarias asociadas
    if company.cuentas_bancarias:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la compañía porque tiene cuentas bancarias asociadas"
        )
    
    db.delete(company)
    db.commit()

@router.get("/", response_model=List[CompaniaListResponse])
async def get_companies(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a retornar"),
    search: Optional[str] = Query(None, description="Buscar por nombre de compañía"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener lista de compañías con filtros opcionales
    """
    query = db.query(Compania)
    
    # Filtro por búsqueda de texto
    if search:
        query = query.filter(
            Compania.nombre.ilike(f"%{search}%")
        )
    
    # Aplicar paginación
    companies = query.offset(skip).limit(limit).all()
    return companies

@router.get("/{company_id}", response_model=CompaniaResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener una compañía específica por ID
    """
    company = db.query(Compania).filter(Compania.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compañía no encontrada"
        )
    return company

@router.post("/", response_model=CompaniaResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompaniaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Crear una nueva compañía
    """
    # Verificar si ya existe una compañía con el mismo nombre
    existing_company = db.query(Compania).filter(
        Compania.nombre.ilike(company_data.nombre)
    ).first()
    
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una compañía con ese nombre"
        )
    
    # Crear nueva compañía
    new_company = Compania(
        nombre=company_data.nombre
    )
    
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    
    return new_company

@router.put("/{company_id}", response_model=CompaniaResponse)
async def update_company(
    company_id: int,
    company_data: CompaniaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Actualizar una compañía existente
    """
    company = db.query(Compania).filter(Compania.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compañía no encontrada"
        )
    
    # Verificar duplicados si se cambia el nombre
    if company_data.nombre and company_data.nombre != company.nombre:
        existing_company = db.query(Compania).filter(
            Compania.nombre.ilike(company_data.nombre),
            Compania.id != company_id
        ).first()
        
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una compañía con ese nombre"
            )
    
    # Actualizar campos
    if company_data.nombre is not None:
        company.nombre = company_data.nombre
    
    db.commit()
    db.refresh(company)
    
    return company

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Eliminar una compañía
    """
    company = db.query(Compania).filter(Compania.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compañía no encontrada"
        )
    
    # Verificar si tiene cuentas bancarias asociadas
    if company.cuentas_bancarias:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la compañía porque tiene cuentas bancarias asociadas"
        )
    
    db.delete(company)
    db.commit()
