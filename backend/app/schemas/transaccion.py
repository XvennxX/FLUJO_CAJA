"""
Schemas Pydantic para el modelo Transaccion
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class TransaccionBase(BaseModel):
    """Schema base para Transaccion"""
    fecha: date
    monto: Decimal
    descripcion: Optional[str] = None
    categoria_id: int
    numero_comprobante: Optional[str] = None
    area_origen: Optional[str] = None
    
    class Config:
        from_attributes = True


class TransaccionCreate(TransaccionBase):
    """Schema para crear una nueva transacción"""
    
    @validator('monto')
    def validate_monto(cls, v):
        if v <= 0:
            raise ValueError('El monto debe ser mayor a cero')
        if v > Decimal('999999999.99'):
            raise ValueError('El monto es demasiado grande')
        return v
    
    @validator('descripcion')
    def validate_descripcion(cls, v):
        if v and len(v.strip()) < 3:
            raise ValueError('La descripción debe tener al menos 3 caracteres')
        return v.strip() if v else v
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "fecha": "2025-01-14",
                "monto": 1500000.00,
                "descripcion": "Pago nómina enero 2025",
                "categoria_id": 5,
                "numero_comprobante": "COM-001-2025",
                "area_origen": "Pagaduría"
            }
        }


class TransaccionUpdate(BaseModel):
    """Schema para actualizar una transacción"""
    fecha: Optional[date] = None
    monto: Optional[Decimal] = None
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    numero_comprobante: Optional[str] = None
    area_origen: Optional[str] = None
    
    @validator('monto')
    def validate_monto(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El monto debe ser mayor a cero')
        return v
    
    class Config:
        from_attributes = True


class TransaccionResponse(TransaccionBase):
    """Schema para la respuesta de Transaccion"""
    id: int
    usuario_id: int
    esta_confirmada: bool
    requiere_aprobacion: bool
    aprobada_por: Optional[int]
    fecha_aprobacion: Optional[datetime]
    creado_en: datetime
    actualizado_en: Optional[datetime]
    
    # Campos calculados
    es_ingreso: bool = False
    es_egreso: bool = False
    monto_formato: str = ""
    flujo_neto: Decimal = Decimal('0')
    
    class Config:
        from_attributes = True


class TransaccionList(BaseModel):
    """Schema para listado de transacciones"""
    transacciones: List[TransaccionResponse]
    total: int
    pagina: int
    por_pagina: int
    total_ingresos: Decimal
    total_egresos: Decimal
    flujo_neto: Decimal
    
    class Config:
        from_attributes = True


class FlujoDiario(BaseModel):
    """Schema para el flujo de caja diario"""
    fecha: date
    ingresos: Decimal
    egresos: Decimal
    flujo_neto: Decimal
    saldo_acumulado: Decimal
    transacciones: List[TransaccionResponse]
    
    class Config:
        from_attributes = True


class FlujoMensual(BaseModel):
    """Schema para el flujo de caja mensual (tipo Excel)"""
    mes: int
    anio: int
    nombre_mes: str
    saldo_inicial: Decimal
    dias: List[FlujoDiario]
    total_ingresos: Decimal
    total_egresos: Decimal
    flujo_neto: Decimal
    saldo_final: Decimal
    
    class Config:
        from_attributes = True
