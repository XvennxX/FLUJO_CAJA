from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    """Schema para solicitud de login"""
    correo: EmailStr
    contraseña: str

class Token(BaseModel):
    """Schema para respuesta de token"""
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    """Schema para datos del token"""
    correo: Optional[str] = None
    user_id: Optional[int] = None
