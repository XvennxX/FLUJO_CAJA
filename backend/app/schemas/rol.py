from pydantic import BaseModel
from datetime import datetime

class RolBase(BaseModel):
    """Schema base para rol"""
    nombre_rol: str
    descripcion: str = None

class RolResponse(RolBase):
    """Schema para respuesta de rol"""
    id_rol: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
