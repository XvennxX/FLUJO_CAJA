"""
Schemas para autenticación JWT
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """Schema para el token de acceso JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: "UsuarioResponse"


class TokenData(BaseModel):
    """Schema para los datos del token"""
    email: Optional[str] = None
    usuario_id: Optional[int] = None


class LoginRequest(BaseModel):
    """Schema para la petición de login"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@flujocaja.com",
                "password": "admin123"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Schema para cambio de contraseña"""
    password_actual: str
    password_nueva: str
    confirmar_password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "password_actual": "password123",
                "password_nueva": "nueva_password123",
                "confirmar_password": "nueva_password123"
            }
        }
