"""
Router de usuarios - CRUD y gestión de usuarios
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.core.database import get_db
from app.routers.auth import get_current_active_user, get_password_hash
from app.models.usuario import Usuario, RolUsuario
from app.schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, 
    UsuarioList, UsuarioStats
)

router = APIRouter()


def verificar_permisos_admin(current_user: Usuario):
    """Verificar que el usuario actual tenga permisos de administrador"""
    if not current_user.es_tesoreria:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción"
        )


@router.get("/", response_model=UsuarioList, summary="Listar usuarios")
async def listar_usuarios(
    pagina: int = Query(1, ge=1, description="Número de página"),
    por_pagina: int = Query(10, ge=1, le=100, description="Elementos por página"),
    buscar: Optional[str] = Query(None, description="Buscar por nombre o email"),
    rol: Optional[RolUsuario] = Query(None, description="Filtrar por rol"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de usuarios con paginación y filtros"""
    verificar_permisos_admin(current_user)
    
    # Construir query base
    query = select(Usuario)
    
    # Aplicar filtros
    if buscar:
        buscar_term = f"%{buscar}%"
        query = query.where(
            (Usuario.nombre.ilike(buscar_term)) | 
            (Usuario.email.ilike(buscar_term))
        )
    
    if rol:
        query = query.where(Usuario.rol == rol)
    
    if activo is not None:
        query = query.where(Usuario.esta_activo == activo)
    
    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Aplicar paginación
    offset = (pagina - 1) * por_pagina
    query = query.offset(offset).limit(por_pagina).order_by(Usuario.nombre)
    
    # Ejecutar query
    result = await db.execute(query)
    usuarios = result.scalars().all()
    
    return UsuarioList(
        usuarios=usuarios,
        total=total,
        pagina=pagina,
        por_pagina=por_pagina
    )


@router.get("/stats", response_model=UsuarioStats, summary="Estadísticas de usuarios")
async def estadisticas_usuarios(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener estadísticas generales de usuarios"""
    verificar_permisos_admin(current_user)
    
    # Total de usuarios
    total_result = await db.execute(select(func.count()).select_from(Usuario))
    total_usuarios = total_result.scalar()
    
    # Usuarios activos
    activos_result = await db.execute(
        select(func.count()).select_from(Usuario).where(Usuario.esta_activo == True)
    )
    usuarios_activos = activos_result.scalar()
    
    # Usuarios por rol
    roles_result = await db.execute(
        select(Usuario.rol, func.count()).group_by(Usuario.rol)
    )
    usuarios_por_rol = {rol.value: count for rol, count in roles_result.all()}
    
    # Último acceso promedio (últimos 30 días)
    ultimo_acceso_result = await db.execute(
        select(func.avg(Usuario.ultimo_acceso)).where(
            Usuario.ultimo_acceso >= func.now() - func.interval('30 days')
        )
    )
    ultimo_acceso_promedio = ultimo_acceso_result.scalar()
    
    return UsuarioStats(
        total_usuarios=total_usuarios,
        usuarios_activos=usuarios_activos,
        usuarios_por_rol=usuarios_por_rol,
        ultimo_acceso_promedio=ultimo_acceso_promedio
    )


@router.get("/{usuario_id}", response_model=UsuarioResponse, summary="Obtener usuario")
async def obtener_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener información de un usuario específico"""
    # Los usuarios pueden ver su propia información, solo admin puede ver otros
    if usuario_id != current_user.id:
        verificar_permisos_admin(current_user)
    
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario


@router.post("/", response_model=UsuarioResponse, summary="Crear usuario")
async def crear_usuario(
    usuario_data: UsuarioCreate,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Crear un nuevo usuario"""
    verificar_permisos_admin(current_user)
    
    # Verificar que el email no exista
    existing_result = await db.execute(select(Usuario).where(Usuario.email == usuario_data.email))
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email"
        )
    
    # Crear usuario
    db_usuario = Usuario(
        nombre=usuario_data.nombre,
        email=usuario_data.email,
        password_hash=get_password_hash(usuario_data.password),
        rol=usuario_data.rol,
        esta_activo=usuario_data.esta_activo,
        creado_por=current_user.id
    )
    
    db.add(db_usuario)
    await db.commit()
    await db.refresh(db_usuario)
    
    return db_usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse, summary="Actualizar usuario")
async def actualizar_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar información de un usuario"""
    # Los usuarios pueden actualizar algunos de sus datos, admin puede actualizar todo
    if usuario_id != current_user.id:
        verificar_permisos_admin(current_user)
    
    # Obtener usuario
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar email único si se está cambiando
    if usuario_data.email and usuario_data.email != usuario.email:
        existing_result = await db.execute(
            select(Usuario).where(
                (Usuario.email == usuario_data.email) & (Usuario.id != usuario_id)
            )
        )
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con este email"
            )
    
    # Actualizar campos permitidos
    update_data = usuario_data.dict(exclude_unset=True)
    
    # Si no es admin, solo puede cambiar ciertos campos
    if usuario_id == current_user.id and not current_user.es_tesoreria:
        allowed_fields = {'nombre', 'preferencias'}
        update_data = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    await db.commit()
    await db.refresh(usuario)
    
    return usuario


@router.delete("/{usuario_id}", summary="Eliminar usuario")
async def eliminar_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Eliminar un usuario (solo desactivar)"""
    verificar_permisos_admin(current_user)
    
    if usuario_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puede eliminar su propio usuario"
        )
    
    # Obtener usuario
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # En lugar de eliminar, desactivamos
    usuario.esta_activo = False
    await db.commit()
    
    return {"mensaje": f"Usuario {usuario.nombre} desactivado exitosamente"}
