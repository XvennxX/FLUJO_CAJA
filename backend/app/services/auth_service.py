from datetime import timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.models.usuario import Usuario
from app.services.audit_service import AuditService

class AuthService:
    """Servicio para manejo de autenticación y autorización"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Autentica un usuario con email y contraseña
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            Dict con información del usuario y token
            
        Raises:
            HTTPException: Si las credenciales son inválidas
        """
        try:
            # Buscar usuario por email
            user = self.db.query(Usuario).filter(
                Usuario.correo == email,
                Usuario.estado == True
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Verificar contraseña
            if not verify_password(password, user.contraseña):
                # Registrar intento fallido
                self.audit_service.registrar_accion(
                    id_usuario=user.id_usuario,
                    accion=f"Intento de login fallido desde {email}",
                    tabla_afectada="usuario"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Crear token de acceso
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user.id_usuario), "correo": user.correo},
                expires_delta=access_token_expires
            )
            
            # Registrar login exitoso
            self.audit_service.registrar_accion(
                id_usuario=user.id_usuario,
                accion="Login exitoso",
                tabla_afectada="usuario"
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user.id_usuario,
                    "nombre": user.nombre_completo,
                    "correo": user.correo,
                    "rol_id": user.id_rol
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno en autenticación: {str(e)}"
            )
    
    def logout_user(self, user_id: int) -> Dict[str, str]:
        """
        Cierra la sesión de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con mensaje de confirmación
        """
        try:
            # Registrar logout
            self.audit_service.registrar_accion(
                id_usuario=user_id,
                accion="Logout",
                tabla_afectada="usuario"
            )
            
            return {"message": "Sesión cerrada exitosamente"}
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al cerrar sesión: {str(e)}"
            )
    
    def validate_user_permissions(self, user_id: int, required_role: str) -> bool:
        """
        Valida si un usuario tiene los permisos necesarios
        
        Args:
            user_id: ID del usuario
            required_role: Rol requerido
            
        Returns:
            True si tiene permisos, False si no
        """
        try:
            user = self.db.query(Usuario).filter(
                Usuario.id_usuario == user_id,
                Usuario.estado == True
            ).first()
            
            if not user or not user.rol:
                return False
            
            # Verificar rol
            return user.rol.nombre_rol == required_role
            
        except Exception:
            return False
