"""
API endpoints para gestión de Roles y Permisos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.roles import Rol, Permiso
from app.models.usuarios import Usuario
from app.schemas.roles import (
    RolCreate, RolUpdate, RolResponse, RolSimple, RolConEstadisticas,
    PermisoCreate, PermisoUpdate, PermisoResponse, PermisosPorModulo,
    AsignarPermisosRequest, RemoverPermisosRequest
)
from sqlalchemy import func

router = APIRouter()

# ========== ENDPOINTS DE ROLES ==========

@router.get("/roles", response_model=List[RolSimple], tags=["Roles"])
def listar_roles(
    skip: int = 0,
    limit: int = 100,
    activo: bool = None,
    db: Session = Depends(get_db)
):
    """Listar todos los roles"""
    query = db.query(Rol)
    
    if activo is not None:
        query = query.filter(Rol.activo == activo)
    
    roles = query.offset(skip).limit(limit).all()
    
    # Agregar cantidad de permisos
    result = []
    for rol in roles:
        rol_dict = RolSimple(
            id=rol.id,
            nombre=rol.nombre,
            codigo=rol.codigo,
            activo=rol.activo,
            es_sistema=rol.es_sistema,
            cant_permisos=len(rol.permisos) if rol.permisos else 0
        )
        result.append(rol_dict)
    
    return result


@router.get("/roles/{rol_id}", response_model=RolConEstadisticas, tags=["Roles"])
def obtener_rol(rol_id: int, db: Session = Depends(get_db)):
    """Obtener un rol por ID con todos sus permisos"""
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {rol_id} no encontrado"
        )
    
    # Contar usuarios asignados a este rol
    cantidad_usuarios = db.query(func.count(Usuario.id)).filter(Usuario.rol_id == rol_id).scalar()
    
    return RolConEstadisticas(
        **rol.to_dict(),
        cantidad_usuarios=cantidad_usuarios,
        cantidad_permisos=len(rol.permisos) if rol.permisos else 0
    )


@router.post("/roles", response_model=RolResponse, status_code=status.HTTP_201_CREATED, tags=["Roles"])
def crear_rol(rol_data: RolCreate, db: Session = Depends(get_db)):
    """Crear un nuevo rol"""
    # Verificar que el código no exista
    existing_rol = db.query(Rol).filter(Rol.codigo == rol_data.codigo).first()
    if existing_rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un rol con el código '{rol_data.codigo}'"
        )
    
    # Verificar que los permisos existan
    if rol_data.permisos_ids:
        permisos = db.query(Permiso).filter(Permiso.id.in_(rol_data.permisos_ids)).all()
        if len(permisos) != len(rol_data.permisos_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Algunos IDs de permisos no son válidos"
            )
    else:
        permisos = []
    
    # Crear el rol
    nuevo_rol = Rol(
        nombre=rol_data.nombre,
        codigo=rol_data.codigo.upper(),  # Código siempre en mayúsculas
        descripcion=rol_data.descripcion,
        activo=rol_data.activo,
        es_sistema=False  # Los roles creados por API no son de sistema
    )
    
    # Asignar permisos
    nuevo_rol.permisos = permisos
    
    db.add(nuevo_rol)
    db.commit()
    db.refresh(nuevo_rol)
    
    return RolResponse(**nuevo_rol.to_dict())


@router.put("/roles/{rol_id}", response_model=RolResponse, tags=["Roles"])
def actualizar_rol(rol_id: int, rol_data: RolUpdate, db: Session = Depends(get_db)):
    """Actualizar un rol existente"""
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {rol_id} no encontrado"
        )
    
    # No permitir editar roles de sistema (protección)
    if rol.es_sistema and (rol_data.activo is False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede desactivar un rol de sistema"
        )
    
    # Actualizar campos
    if rol_data.nombre is not None:
        rol.nombre = rol_data.nombre
    if rol_data.descripcion is not None:
        rol.descripcion = rol_data.descripcion
    if rol_data.activo is not None:
        rol.activo = rol_data.activo
    
    # Actualizar permisos si se proporcionan
    if rol_data.permisos_ids is not None:
        permisos = db.query(Permiso).filter(Permiso.id.in_(rol_data.permisos_ids)).all()
        if len(permisos) != len(rol_data.permisos_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Algunos IDs de permisos no son válidos"
            )
        rol.permisos = permisos
    
    db.commit()
    db.refresh(rol)
    
    return RolResponse(**rol.to_dict())


@router.delete("/roles/{rol_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Roles"])
def eliminar_rol(rol_id: int, db: Session = Depends(get_db)):
    """Eliminar un rol"""
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {rol_id} no encontrado"
        )
    
    # No permitir eliminar roles de sistema
    if rol.es_sistema:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede eliminar un rol de sistema"
        )
    
    # Verificar si hay usuarios asignados
    usuarios_asignados = db.query(func.count(Usuario.id)).filter(Usuario.rol_id == rol_id).scalar()
    if usuarios_asignados > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el rol porque tiene {usuarios_asignados} usuario(s) asignado(s)"
        )
    
    db.delete(rol)
    db.commit()


# ========== ENDPOINTS DE PERMISOS ==========

@router.get("/permisos", response_model=List[PermisoResponse], tags=["Permisos"])
def listar_permisos(
    skip: int = 0,
    limit: int = 200,
    modulo: str = None,
    activo: bool = None,
    db: Session = Depends(get_db)
):
    """Listar todos los permisos"""
    query = db.query(Permiso)
    
    if modulo:
        query = query.filter(Permiso.modulo == modulo)
    if activo is not None:
        query = query.filter(Permiso.activo == activo)
    
    permisos = query.order_by(Permiso.modulo, Permiso.nombre).offset(skip).limit(limit).all()
    return [PermisoResponse(**p.to_dict()) for p in permisos]


@router.get("/permisos/por-modulo", response_model=List[PermisosPorModulo], tags=["Permisos"])
def listar_permisos_por_modulo(db: Session = Depends(get_db)):
    """Listar permisos agrupados por módulo"""
    permisos = db.query(Permiso).filter(Permiso.activo == True).order_by(Permiso.modulo, Permiso.nombre).all()
    
    # Agrupar por módulo
    modulos_dict = {}
    for permiso in permisos:
        if permiso.modulo not in modulos_dict:
            modulos_dict[permiso.modulo] = []
        modulos_dict[permiso.modulo].append(PermisoResponse(**permiso.to_dict()))
    
    # Convertir a lista
    result = [
        PermisosPorModulo(modulo=modulo, permisos=permisos)
        for modulo, permisos in sorted(modulos_dict.items())
    ]
    
    return result


@router.get("/permisos/{permiso_id}", response_model=PermisoResponse, tags=["Permisos"])
def obtener_permiso(permiso_id: int, db: Session = Depends(get_db)):
    """Obtener un permiso por ID"""
    permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    
    if not permiso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permiso con ID {permiso_id} no encontrado"
        )
    
    return PermisoResponse(**permiso.to_dict())


@router.post("/permisos", response_model=PermisoResponse, status_code=status.HTTP_201_CREATED, tags=["Permisos"])
def crear_permiso(permiso_data: PermisoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo permiso"""
    # Verificar que el código no exista
    existing_permiso = db.query(Permiso).filter(Permiso.codigo == permiso_data.codigo).first()
    if existing_permiso:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un permiso con el código '{permiso_data.codigo}'"
        )
    
    nuevo_permiso = Permiso(
        nombre=permiso_data.nombre,
        codigo=permiso_data.codigo,
        descripcion=permiso_data.descripcion,
        modulo=permiso_data.modulo,
        activo=permiso_data.activo
    )
    
    db.add(nuevo_permiso)
    db.commit()
    db.refresh(nuevo_permiso)
    
    return PermisoResponse(**nuevo_permiso.to_dict())


@router.put("/permisos/{permiso_id}", response_model=PermisoResponse, tags=["Permisos"])
def actualizar_permiso(permiso_id: int, permiso_data: PermisoUpdate, db: Session = Depends(get_db)):
    """Actualizar un permiso existente"""
    permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    
    if not permiso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permiso con ID {permiso_id} no encontrado"
        )
    
    # Actualizar campos
    if permiso_data.nombre is not None:
        permiso.nombre = permiso_data.nombre
    if permiso_data.descripcion is not None:
        permiso.descripcion = permiso_data.descripcion
    if permiso_data.modulo is not None:
        permiso.modulo = permiso_data.modulo
    if permiso_data.activo is not None:
        permiso.activo = permiso_data.activo
    
    db.commit()
    db.refresh(permiso)
    
    return PermisoResponse(**permiso.to_dict())


@router.delete("/permisos/{permiso_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Permisos"])
def eliminar_permiso(permiso_id: int, db: Session = Depends(get_db)):
    """Eliminar un permiso"""
    permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    
    if not permiso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permiso con ID {permiso_id} no encontrado"
        )
    
    # Verificar si está asignado a algún rol
    roles_asignados = len(permiso.roles) if permiso.roles else 0
    if roles_asignados > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el permiso porque está asignado a {roles_asignados} rol(es)"
        )
    
    db.delete(permiso)
    db.commit()


# ========== ASIGNACIÓN DE PERMISOS A ROLES ==========

@router.post("/roles/{rol_id}/permisos", response_model=RolResponse, tags=["Roles"])
def asignar_permisos_a_rol(rol_id: int, request: AsignarPermisosRequest, db: Session = Depends(get_db)):
    """Asignar permisos a un rol (agrega sin remover existentes)"""
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {rol_id} no encontrado"
        )
    
    # Obtener permisos
    permisos = db.query(Permiso).filter(Permiso.id.in_(request.permisos_ids)).all()
    if len(permisos) != len(request.permisos_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Algunos IDs de permisos no son válidos"
        )
    
    # Agregar permisos sin duplicados
    permisos_actuales_ids = {p.id for p in rol.permisos}
    for permiso in permisos:
        if permiso.id not in permisos_actuales_ids:
            rol.permisos.append(permiso)
    
    db.commit()
    db.refresh(rol)
    
    return RolResponse(**rol.to_dict())


@router.delete("/roles/{rol_id}/permisos", response_model=RolResponse, tags=["Roles"])
def remover_permisos_de_rol(rol_id: int, request: RemoverPermisosRequest, db: Session = Depends(get_db)):
    """Remover permisos de un rol"""
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {rol_id} no encontrado"
        )
    
    # Filtrar permisos
    rol.permisos = [p for p in rol.permisos if p.id not in request.permisos_ids]
    
    db.commit()
    db.refresh(rol)
    
    return RolResponse(**rol.to_dict())
