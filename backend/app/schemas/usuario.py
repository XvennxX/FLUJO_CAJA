"""
Schemas Pydantic para el modelo Usuario
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.models.usuario import RolUsuario


class UsuarioBase(BaseModel):
    """Schema base para Usuario"""
    nombre: str
    email: EmailStr
    rol: RolUsuario
    esta_activo: bool = True
    
    class Config:
        from_attributes = True


class UsuarioCreate(UsuarioBase):
    """Schema para crear un nuevo usuario"""
    password: str
    confirmar_password: str
    
    @validator('confirmar_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "nombre": "Ana García",
                "email": "ana.garcia@empresa.com",
                "rol": "tesoreria",
                "password": "password123",
                "confirmar_password": "password123",
                "esta_activo": True
            }
        }


class UsuarioUpdate(BaseModel):
    """Schema para actualizar un usuario"""
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[RolUsuario] = None
    esta_activo: Optional[bool] = None
    preferencias: Optional[str] = None
    
    class Config:
        from_attributes = True


class UsuarioResponse(UsuarioBase):
    """Schema para la respuesta de Usuario (sin password)"""
    id: int
    primer_login: bool
    ultimo_acceso: Optional[datetime]
    creado_en: datetime
    actualizado_en: Optional[datetime]
    preferencias: Optional[str]
    
    class Config:
        from_attributes = True


class UsuarioList(BaseModel):
    """Schema para listado de usuarios"""
    usuarios: List[UsuarioResponse]
    total: int
    pagina: int
    por_pagina: int
    
    class Config:
        from_attributes = True


class UsuarioStats(BaseModel):
    """Schema para estadísticas de usuario"""
    total_usuarios: int
    usuarios_activos: int
    usuarios_por_rol: dict
    ultimo_acceso_promedio: Optional[datetime]
    
    class Config:
        from_attributes = True
