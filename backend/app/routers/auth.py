"""
Router de autenticación - Login, logout, refresh token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.database import get_db
from app.core.config import settings
from app.schemas.auth import Token, LoginRequest, ChangePasswordRequest
from app.schemas.usuario import UsuarioResponse
from app.models.usuario import Usuario

router = APIRouter()

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """Obtener usuario actual desde el token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    from sqlalchemy import select
    result = await db.execute(select(Usuario).where(Usuario.email == email))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    # Actualizar último acceso
    user.ultimo_acceso = datetime.utcnow()
    await db.commit()
    
    return user


async def get_current_active_user(current_user: Usuario = Depends(get_current_user)):
    """Obtener usuario activo actual"""
    if not current_user.esta_activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


@router.post("/login", response_model=Token, summary="Iniciar sesión")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Iniciar sesión en el sistema
    
    - **username**: Email del usuario
    - **password**: Contraseña del usuario
    """
    from sqlalchemy import select
    
    # Buscar usuario por email
    result = await db.execute(select(Usuario).where(Usuario.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
        )
    
    # Crear token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Actualizar último acceso y primer login
    user.ultimo_acceso = datetime.utcnow()
    if user.primer_login:
        user.primer_login = False
    
    await db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "usuario": UsuarioResponse.from_orm(user)
    }


@router.post("/logout", summary="Cerrar sesión")
async def logout(current_user: Usuario = Depends(get_current_active_user)):
    """
    Cerrar sesión del usuario actual
    En esta implementación básica solo retornamos confirmación
    En producción podrías implementar blacklist de tokens
    """
    return {"mensaje": f"Sesión cerrada para {current_user.nombre}"}


@router.get("/me", response_model=UsuarioResponse, summary="Información del usuario actual")
async def read_users_me(current_user: Usuario = Depends(get_current_active_user)):
    """Obtener información del usuario autenticado actual"""
    return current_user


@router.post("/change-password", summary="Cambiar contraseña")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cambiar la contraseña del usuario actual"""
    
    # Verificar contraseña actual
    if not verify_password(request.password_actual, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Verificar que las nuevas contraseñas coincidan
    if request.password_nueva != request.confirmar_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las nuevas contraseñas no coinciden"
        )
    
    # Actualizar contraseña
    current_user.password_hash = get_password_hash(request.password_nueva)
    await db.commit()
    
    return {"mensaje": "Contraseña actualizada exitosamente"}


@router.post("/refresh", response_model=Token, summary="Renovar token")
async def refresh_token(current_user: Usuario = Depends(get_current_active_user)):
    """Renovar el token de acceso"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer", 
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "usuario": UsuarioResponse.from_orm(current_user)
    }
