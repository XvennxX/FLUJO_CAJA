from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.schemas.auth import Token, LoginRequest

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Autenticar usuario y generar token JWT"""
    
    # Crear servicios
    audit_service = AuditService(db)
    auth_service = AuthService(db, audit_service)
    
    try:
        # Autenticar usuario
        result = auth_service.authenticate_user(
            correo=form_data.username,
            contraseña=form_data.password
        )
        
        return {
            "access_token": result["access_token"],
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/logout")
async def logout(
    db: Session = Depends(get_db),
    current_user: dict = Depends(oauth2_scheme)
):
    """Cerrar sesión del usuario"""
    
    # Crear servicios
    audit_service = AuditService(db)
    auth_service = AuthService(db, audit_service)
    
    try:
        # Obtener ID del usuario del token
        from app.core.security import decode_access_token
        user_data = decode_access_token(current_user)
        user_id = int(user_data.get("sub"))
        
        # Registrar logout
        result = auth_service.logout_user(user_id)
        
        return result
        
    except Exception as e:
        return {"message": "Sesión cerrada exitosamente"}
