from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from ..core.database import get_db
from ..models.usuarios import Usuario
from ..schemas.auth import UserResponse, UserCreate, UserUpdate
from ..services.auth_service import get_current_user, check_user_role, get_password_hash
from ..services.auditoria_service import AuditoriaService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador"]))
):
    """Obtener lista de usuarios (solo administradores)"""
    users = db.query(Usuario).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador"]))
):
    """Obtener usuario por ID (solo administradores)"""
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador"]))
):
    """Actualizar usuario (solo administradores)"""
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Guardar valores anteriores para auditoría
    valores_anteriores = {
        "nombre": user.nombre,
        "email": user.email,
        "rol": user.rol
    }
    
    # Actualizar campos proporcionados
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Si se proporciona nueva contraseña, hashearla
    if "password" in update_data:
        update_data["contrasena"] = get_password_hash(update_data.pop("password"))
        valores_anteriores["password"] = "***"  # No guardar contraseñas en auditoría
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # 📝 AUDITORÍA: Registrar actualización de usuario
    try:
        valores_nuevos = {
            "nombre": user.nombre,
            "email": user.email,
            "rol": user.rol
        }
        if "contrasena" in update_data:
            valores_nuevos["password"] = "*** (actualizada)"
        
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="UPDATE",
            modulo="USUARIOS",
            entidad="Usuario",
            entidad_id=str(user.id),
            descripcion=f"Actualizó perfil de usuario: {user.nombre}",
            valores_anteriores=valores_anteriores,
            valores_nuevos=valores_nuevos
        )
        logger.info(f"✅ Auditoría registrada: UPDATE usuario {user.id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de actualización de usuario: {e}")
    
    return UserResponse.model_validate(user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador"]))
):
    """Eliminar usuario (solo administradores)"""
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # No permitir eliminar al usuario actual
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Guardar datos para auditoría antes de eliminar
    nombre_eliminado = user.nombre
    email_eliminado = user.email
    rol_eliminado = user.rol
    
    db.delete(user)
    db.commit()
    
    # 📝 AUDITORÍA: Registrar eliminación de usuario
    try:
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="DELETE",
            modulo="USUARIOS",
            entidad="Usuario",
            entidad_id=str(user_id),
            descripcion=f"Eliminó usuario: {nombre_eliminado} ({email_eliminado})",
            valores_anteriores={
                "nombre": nombre_eliminado,
                "email": email_eliminado,
                "rol": rol_eliminado
            }
        )
        logger.info(f"✅ Auditoría registrada: DELETE usuario {user_id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de eliminación de usuario: {e}")
    
    return {"message": "User deleted successfully"}