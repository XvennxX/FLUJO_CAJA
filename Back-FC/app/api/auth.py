from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.config import get_settings
from ..schemas.auth import Token, UserLogin, UserResponse, UserCreate
from ..services.auth_service import (
    authenticate_user, 
    create_access_token, 
    get_current_user,
    get_password_hash
)
from ..models.usuarios import Usuario

router = APIRouter(prefix="/auth", tags=["authentication"])
settings = get_settings()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Iniciar sesión y obtener token de acceso"""
    # Primero verificar si el usuario existe
    user_in_db = db.query(Usuario).filter(Usuario.email == user_credentials.email).first()
    
    if user_in_db and not user_in_db.estado:
        # Usuario existe pero está inactivo
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Su cuenta ha sido desactivada. Contacte al administrador.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Ahora intentar autenticar (incluye verificación de contraseña y estado)
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": UserResponse.model_validate(user)
    }

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Registrar nuevo usuario"""
    # Verificar si el usuario ya existe
    existing_user = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    new_user = Usuario(
        nombre=user_data.nombre,
        email=user_data.email,
        contrasena=hashed_password,
        rol=user_data.rol
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse.model_validate(new_user)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return UserResponse.model_validate(current_user)

@router.post("/logout")
async def logout():
    """Cerrar sesión (en el cliente se debe eliminar el token)"""
    return {"message": "Successfully logged out"}