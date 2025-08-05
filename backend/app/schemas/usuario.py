from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    """Schema base para usuario"""
    nombre_completo: str
    correo: EmailStr
    id_rol: int

class UsuarioCreate(UsuarioBase):
    """Schema para crear usuario"""
    contraseña: str

class UsuarioUpdate(BaseModel):
    """Schema para actualizar usuario"""
    nombre_completo: Optional[str] = None
    correo: Optional[EmailStr] = None
    id_rol: Optional[int] = None

class UsuarioResponse(UsuarioBase):
    """Schema para respuesta de usuario"""
    id_usuario: int
    estado: bool
    ultimo_acceso: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UsuarioEstado(BaseModel):
    """Schema para cambiar estado de usuario"""
    estado: bool
