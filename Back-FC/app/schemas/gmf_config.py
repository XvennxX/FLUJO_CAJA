"""
Schemas Pydantic para la configuración GMF
"""
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

class GMFConfigBase(BaseModel):
    """Schema base para GMF Config"""
    cuenta_bancaria_id: int
    conceptos_seleccionados: List[int]  # IDs de conceptos

class GMFConfigCreate(GMFConfigBase):
    """Schema para crear configuración GMF"""
    pass

class GMFConfigUpdate(BaseModel):
    """Schema para actualizar configuración GMF"""
    conceptos_seleccionados: List[int]  # IDs de conceptos
    activo: Optional[bool] = True

class GMFConfigResponse(GMFConfigBase):
    """Schema de respuesta para configuración GMF"""
    id: int
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True
