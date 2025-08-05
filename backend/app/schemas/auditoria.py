"""
Schemas para auditoría
"""
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AuditoriaBase(BaseModel):
    """Schema base para auditoría"""
    id_usuario: int
    accion: str
    tabla_afectada: str
    id_registro: Optional[int] = None
    descripcion: Optional[str] = None


class AuditoriaCreate(AuditoriaBase):
    """Schema para crear registro de auditoría"""
    fecha_hora: datetime


class AuditoriaUpdate(BaseModel):
    """Schema para actualizar registro de auditoría"""
    descripcion: Optional[str] = None


class AuditoriaResponse(AuditoriaBase):
    """Schema para respuesta de auditoría"""
    id_auditoria: int
    fecha_hora: datetime
    nombre_usuario: Optional[str] = None
    
    class Config:
        from_attributes = True
