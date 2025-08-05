from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, validator
from typing import Optional

class IngresoBase(BaseModel):
    """Schema base para ingresos"""
    valor: Decimal
    fecha: date
    id_cuenta: int
    id_concepto: int
    
    @validator('valor')
    def validate_valor(cls, v):
        if v <= 0:
            raise ValueError('El valor debe ser positivo')
        return v

class IngresoCreate(IngresoBase):
    """Schema para crear ingreso"""
    pass

class IngresoUpdate(BaseModel):
    """Schema para actualizar ingreso"""
    valor: Optional[Decimal] = None
    fecha: Optional[date] = None
    id_cuenta: Optional[int] = None
    id_concepto: Optional[int] = None
    
    @validator('valor')
    def validate_valor(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El valor debe ser positivo')
        return v

class IngresoResponse(IngresoBase):
    """Schema para respuesta de ingreso"""
    id_ingreso: int
    nombre_cuenta: Optional[str] = None
    nombre_concepto: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EgresoBase(BaseModel):
    """Schema base para egresos"""
    valor: Decimal
    fecha: date
    id_cuenta: int
    id_concepto: int
    
    @validator('valor')
    def validate_valor(cls, v):
        if v <= 0:
            raise ValueError('El valor debe ser positivo')
        return v

class EgresoCreate(EgresoBase):
    """Schema para crear egreso"""
    pass

class EgresoUpdate(BaseModel):
    """Schema para actualizar egreso"""
    valor: Optional[Decimal] = None
    fecha: Optional[date] = None
    id_cuenta: Optional[int] = None
    id_concepto: Optional[int] = None
    
    @validator('valor')
    def validate_valor(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El valor debe ser positivo')
        return v

class EgresoResponse(EgresoBase):
    """Schema para respuesta de egreso"""
    id_egreso: int
    nombre_cuenta: Optional[str] = None
    nombre_concepto: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TransaccionResumen(BaseModel):
    """Schema para resumen de transacciones"""
    total_ingresos: Decimal
    total_egresos: Decimal
    balance: Decimal
    cantidad_ingresos: int
    cantidad_egresos: int
    fecha_inicio: date
    fecha_fin: date
