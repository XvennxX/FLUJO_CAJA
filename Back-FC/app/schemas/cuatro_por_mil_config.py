"""
Schemas Pydantic para la configuración de Cuatro por Mil con versionado histórico
Similar a gmf_config.py pero para el área de Pagaduría
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date


class CuatroPorMilConfigBase(BaseModel):
    """Schema base para Cuatro por Mil Config"""
    cuenta_bancaria_id: int
    conceptos_seleccionados: List[int]  # IDs de conceptos


class CuatroPorMilConfigCreate(CuatroPorMilConfigBase):
    """Schema para crear configuración Cuatro por Mil con fecha de vigencia"""
    fecha_vigencia_desde: date  # Desde qué fecha aplica esta configuración


class CuatroPorMilConfigUpdate(BaseModel):
    """Schema para actualizar configuración Cuatro por Mil"""
    conceptos_seleccionados: List[int]  # IDs de conceptos
    fecha_vigencia_desde: Optional[date] = None  # Si se modifica, desde qué fecha aplica
    activo: Optional[bool] = True


class CuatroPorMilConfigResponse(CuatroPorMilConfigBase):
    """Schema de respuesta para configuración Cuatro por Mil"""
    id: int
    activo: bool
    fecha_vigencia_desde: date  # Desde cuándo es válida esta config
    fecha_creacion: Optional[datetime] = None  # Cuándo se creó el registro (None si es config por defecto)
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True
