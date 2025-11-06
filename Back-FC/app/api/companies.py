from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
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
from ..services.auth_service import get_current_user_optional
from ..services.auditoria_service import AuditoriaService
from ..models.usuarios import Usuario
import logging

logger = logging.getLogger(__name__)
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
    request: Request,
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

    # 📝 AUDITORÍA (test): Registrar creación de empresa
    try:
        # Intentar obtener usuario autenticado, sino usar usuario por defecto
        current_user = await get_current_user_optional(request, db)
        
        if not current_user:
            # Si no hay usuario autenticado, usar usuario por defecto
            current_user = db.query(Usuario).filter(Usuario.email == "admin@sifco.com").first()
            if not current_user:
                # Si no existe el admin, crear un usuario temporal para auditoría
                current_user = type('Usuario', (), {
                    'id': 1,
                    'nombre': 'Sistema Test',
                    'email': 'sistema@test.com'
                })()
        
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="CREATE",
            modulo="EMPRESAS",
            entidad="Compania",
            entidad_id=str(new_company.id),
            descripcion=f"Creó empresa: {new_company.nombre}",
            valores_nuevos={"nombre": new_company.nombre}
        )
        logger.info(f"✅ Auditoría registrada: CREATE empresa {new_company.id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de creación de empresa: {e}")

    return new_company

# Endpoint temporal para actualizar sin autenticación
@router.put("/test/{company_id}", response_model=CompaniaResponse)
async def update_company_test(
    company_id: int,
    company_data: CompaniaUpdate,
    request: Request,
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
    
    # Guardar valor anterior para auditoría
    nombre_anterior = company.nombre

    # Actualizar campos
    if company_data.nombre is not None:
        company.nombre = company_data.nombre
    
    db.commit()
    db.refresh(company)

    # 📝 AUDITORÍA (test): Registrar actualización de empresa
    try:
        # Intentar obtener usuario autenticado, sino usar usuario por defecto
        current_user = await get_current_user_optional(request, db)
        
        if not current_user:
            # Si no hay usuario autenticado, usar usuario por defecto
            current_user = db.query(Usuario).filter(Usuario.email == "admin@sifco.com").first()
            if not current_user:
                # Si no existe el admin, crear un usuario temporal para auditoría
                current_user = type('Usuario', (), {
                    'id': 1,
                    'nombre': 'Sistema Test',
                    'email': 'sistema@test.com'
                })()
        
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="UPDATE",
            modulo="EMPRESAS",
            entidad="Compania",
            entidad_id=str(company.id),
            descripcion=f"Actualizó empresa: {nombre_anterior} → {company.nombre}" if nombre_anterior != company.nombre else f"Actualizó empresa: {company.nombre}",
            valores_anteriores={"nombre": nombre_anterior},
            valores_nuevos={"nombre": company.nombre}
        )
        logger.info(f"✅ Auditoría registrada: UPDATE empresa {company.id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de actualización de empresa: {e}")

    return company

# Endpoint temporal para eliminar sin autenticación
@router.delete("/test/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_test(
    company_id: int,
    request: Request,
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
    
    # Guardar para auditoría
    nombre_eliminado = company.nombre

    db.delete(company)
    db.commit()

    # 📝 AUDITORÍA (test): Registrar eliminación de empresa
    try:
        # Intentar obtener usuario autenticado, sino usar usuario por defecto
        current_user = await get_current_user_optional(request, db)
        
        if not current_user:
            # Si no hay usuario autenticado, usar usuario por defecto
            current_user = db.query(Usuario).filter(Usuario.email == "admin@sifco.com").first()
            if not current_user:
                # Si no existe el admin, crear un usuario temporal para auditoría
                current_user = type('Usuario', (), {
                    'id': 1,
                    'nombre': 'Sistema Test',
                    'email': 'sistema@test.com'
                })()
        
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="DELETE",
            modulo="EMPRESAS",
            entidad="Compania",
            entidad_id=str(company_id),
            descripcion=f"Eliminó empresa: {nombre_eliminado}",
            valores_anteriores={"nombre": nombre_eliminado}
        )
        logger.info(f"✅ Auditoría registrada: DELETE empresa {company_id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de eliminación de empresa: {e}")

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
    
    # 📝 AUDITORÍA: Registrar creación de empresa
    try:
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="CREATE",
            modulo="EMPRESAS",
            entidad="Compania",
            entidad_id=str(new_company.id),
            descripcion=f"Creó empresa: {new_company.nombre}",
            valores_nuevos={"nombre": new_company.nombre}
        )
        logger.info(f"✅ Auditoría registrada: CREATE empresa {new_company.id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de creación de empresa: {e}")
    
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
    
    # Guardar valor anterior para auditoría
    nombre_anterior = company.nombre
    
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
    
    # 📝 AUDITORÍA: Registrar actualización de empresa
    try:
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="UPDATE",
            modulo="EMPRESAS",
            entidad="Compania",
            entidad_id=str(company.id),
            descripcion=f"Actualizó empresa: {nombre_anterior} → {company.nombre}" if nombre_anterior != company.nombre else f"Actualizó empresa: {company.nombre}",
            valores_anteriores={"nombre": nombre_anterior},
            valores_nuevos={"nombre": company.nombre}
        )
        logger.info(f"✅ Auditoría registrada: UPDATE empresa {company.id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de actualización de empresa: {e}")
    
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
    
    # Guardar datos para auditoría antes de eliminar
    nombre_eliminado = company.nombre
    
    db.delete(company)
    db.commit()
    
    # 📝 AUDITORÍA: Registrar eliminación de empresa
    try:
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="DELETE",
            modulo="EMPRESAS",
            entidad="Compania",
            entidad_id=str(company_id),
            descripcion=f"Eliminó empresa: {nombre_eliminado}",
            valores_anteriores={"nombre": nombre_eliminado}
        )
        logger.info(f"✅ Auditoría registrada: DELETE empresa {company_id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de eliminación de empresa: {e}")
