from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.config import get_settings
from ..core.database import get_db
from ..models.usuarios import Usuario
from ..schemas.auth import TokenData

settings = get_settings()

# Configuración de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de seguridad
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Obtener hash de contraseña"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str) -> Optional[Usuario]:
    """Autenticar usuario"""
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.contrasena):
        return None
    # Verificar que el usuario esté activo
    if not user.estado:
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token de acceso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """Obtener usuario actual desde el token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(Usuario).filter(Usuario.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_optional(
    request,
    db: Session
) -> Optional[Usuario]:
    """Obtener usuario actual de manera opcional (sin lanzar excepción si no está autenticado)"""
    try:
        # Intentar obtener el token del header Authorization
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
            
        user = db.query(Usuario).filter(Usuario.email == email).first()
        return user
    except:
        return None

def check_user_role(required_roles: list[str]):
    """Decorador para verificar roles de usuario"""
    def role_checker(current_user: Usuario = Depends(get_current_user)):
        if current_user.rol not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso"
            )
        return current_user
    return role_checker

def get_current_user_from_token(token: str, db: Session) -> Optional[Usuario]:
    """Obtener usuario desde token sin usar FastAPI dependencies"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
        
        user = db.query(Usuario).filter(Usuario.email == email).first()
        return user
    except JWTError:
        return None