"""
Schemas Pydantic para el modelo Categoria
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from app.models.categoria import TipoCategoria


class CategoriaBase(BaseModel):
    """Schema base para Categoria"""
    nombre: str
    descripcion: Optional[str] = None
    tipo: TipoCategoria
    esta_activa: bool = True
    codigo_contable: Optional[str] = None
    color: str = "#6B7280"
    orden: int = 0
    
    class Config:
        from_attributes = True


class CategoriaCreate(CategoriaBase):
    """Schema para crear una nueva categoría"""
    
    @validator('nombre')
    def validate_nombre(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        return v.strip().title()
    
    @validator('color')
    def validate_color(cls, v):
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('El color debe ser un código hexadecimal válido (#RRGGBB)')
        return v.upper()
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "nombre": "Servicios Tecnológicos",
                "descripcion": "Ingresos por servicios de tecnología y consultoría",
                "tipo": "ingreso",
                "codigo_contable": "4250",
                "color": "#10B981",
                "orden": 10,
                "esta_activa": True
            }
        }


class CategoriaUpdate(BaseModel):
    """Schema para actualizar una categoría"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    esta_activa: Optional[bool] = None
    codigo_contable: Optional[str] = None
    color: Optional[str] = None
    orden: Optional[int] = None
    
    @validator('nombre')
    def validate_nombre(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        return v.strip().title() if v else v
    
    @validator('color')
    def validate_color(cls, v):
        if v and (not v.startswith('#') or len(v) != 7):
            raise ValueError('El color debe ser un código hexadecimal válido (#RRGGBB)')
        return v.upper() if v else v
    
    class Config:
        from_attributes = True


class CategoriaResponse(CategoriaBase):
    """Schema para la respuesta de Categoria"""
    id: int
    es_categoria_sistema: bool
    total_transacciones: int = 0
    creado_en: datetime
    actualizado_en: Optional[datetime]
    
    class Config:
        from_attributes = True


class CategoriaList(BaseModel):
    """Schema para listado de categorías"""
    categorias: List[CategoriaResponse]
    total: int
    ingresos: int
    egresos: int
    
    class Config:
        from_attributes = True


class CategoriaStats(BaseModel):
    """Schema para estadísticas de categoría"""
    categoria_id: int
    categoria_nombre: str
    total_transacciones: int
    monto_total: float
    promedio_mensual: float
    ultimo_movimiento: Optional[datetime]
    
    class Config:
        from_attributes = True


class CategoriaResumen(BaseModel):
    """Schema para resumen de categorías por tipo"""
    tipo: TipoCategoria
    categorias: List[CategoriaResponse]
    total_categorias: int
    total_transacciones: int
    monto_total: float
    
    class Config:
        from_attributes = True
