from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.user_service import UserService
from app.services.audit_service import AuditService
from app.schemas.usuario import UsuarioResponse, UsuarioCreate, UsuarioUpdate, UsuarioEstado

router = APIRouter()

@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db)
):
    """Listar todos los usuarios (solo administradores)"""
    
    # Crear servicios
    audit_service = AuditService(db)
    user_service = UserService(db, audit_service)
    
    try:
        usuarios = user_service.listar_usuarios(
            skip=skip,
            limit=limit,
            incluir_inactivos=incluir_inactivos
        )
        
        return usuarios
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar usuarios: {str(e)}"
        )

@router.post("/", response_model=UsuarioResponse)
async def crear_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario (solo administradores)"""
    
    # Crear servicios
    audit_service = AuditService(db)
    user_service = UserService(db, audit_service)
    
    try:
        # TODO: Obtener usuario actual del token
        user_id = 1  # Temporal
        
        nuevo_usuario = user_service.crear_usuario(
            usuario_data=usuario,
            user_id=user_id
        )
        
        return nuevo_usuario
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )

@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un usuario por ID"""
    
    # Crear servicios
    audit_service = AuditService(db)
    user_service = UserService(db, audit_service)
    
    try:
        usuario = user_service.obtener_usuario(usuario_id)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return usuario
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}"
        )

@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar usuario"""
    
    # Crear servicios
    audit_service = AuditService(db)
    user_service = UserService(db, audit_service)
    
    try:
        # TODO: Obtener usuario actual del token
        user_id = 1  # Temporal
        
        usuario_actualizado = user_service.actualizar_usuario(
            usuario_id=usuario_id,
            usuario_data=usuario_update,
            user_id=user_id
        )
        
        return usuario_actualizado
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar usuario: {str(e)}"
        )
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar campos
    update_data = usuario_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    db.commit()
    db.refresh(usuario)
    
    return usuario

@router.patch("/{usuario_id}/estado", response_model=UsuarioResponse)
async def cambiar_estado_usuario(
    usuario_id: int,
    estado_update: UsuarioEstado,
    db: Session = Depends(get_db)
):
    """Activar o desactivar usuario"""
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    usuario.estado = estado_update.estado
    db.commit()
    db.refresh(usuario)
    
    return usuario
