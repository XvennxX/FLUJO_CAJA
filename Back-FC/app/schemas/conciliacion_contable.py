"""
Schemas para la conciliación contable
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import date

class ConciliacionContableBase(BaseModel):
    fecha: date = Field(..., description="Fecha de la conciliación")
    empresa_id: int = Field(..., description="ID de la empresa")
    total_centralizadora: Optional[Decimal] = Field(None, description="Total centralizadora manual")
    estado: str = Field("Pendiente", description="Estado de la conciliación")
    observaciones: Optional[str] = Field(None, description="Observaciones")

class ConciliacionContableCreate(ConciliacionContableBase):
    pass

class ConciliacionContableUpdate(BaseModel):
    total_centralizadora: Optional[Decimal] = Field(None, description="Total centralizadora manual")
    estado: Optional[str] = Field(None, description="Estado de la conciliación")
    observaciones: Optional[str] = Field(None, description="Observaciones")

class ConciliacionContableResponse(ConciliacionContableBase):
    id: int
    total_pagaduria: Decimal
    total_tesoreria: Decimal
    diferencia: Optional[Decimal]
    
    # Propiedades calculadas
    total_calculado: Decimal
    estado_conciliacion: str
    
    class Config:
        from_attributes = True

class CompaniaResponse(BaseModel):
    """Información básica de la compañía"""
    id: int
    nombre: str
    
    class Config:
        from_attributes = True

class EmpresaConciliacionResponse(BaseModel):
    """Respuesta para mostrar empresas con sus datos de conciliación"""
    id: int
    compania_id: int
    compania: CompaniaResponse
    total_pagaduria: Decimal = Field(default=0, description="Total Pagaduría")
    total_tesoreria: Decimal = Field(default=0, description="Total Tesorería") 
    total_calculado: Decimal = Field(default=0, description="Total calculado (Pagaduría + Tesorería)")
    total_centralizadora: Optional[Decimal] = Field(None, description="Total centralizadora manual")
    diferencia: Decimal = Field(default=0, description="Diferencia entre total y centralizadora")
    estado: str = Field(default="pendiente", description="Estado de la conciliación")
    observaciones: Optional[str] = Field(None, description="Observaciones")
    
    class Config:
        from_attributes = True

class ConciliacionFechaRequest(BaseModel):
    """Request para obtener conciliación por fecha"""
    fecha: date = Field(..., description="Fecha de conciliación a consultar")

class ConciliacionFechaResponse(BaseModel):
    """Response con todas las empresas para una fecha específica"""
    fecha: date
    empresas: List[EmpresaConciliacionResponse]
    
    class Config:
        from_attributes = True