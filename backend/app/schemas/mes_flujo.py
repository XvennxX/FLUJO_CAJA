"""
Schemas Pydantic para el modelo MesFlujo
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class MesFlujBase(BaseModel):
    """Schema base para MesFlujo"""
    mes: int
    anio: int
    saldo_inicial: Decimal
    observaciones: Optional[str] = None
    
    @validator('mes')
    def validate_mes(cls, v):
        if v < 1 or v > 12:
            raise ValueError('El mes debe estar entre 1 y 12')
        return v
    
    @validator('anio')
    def validate_anio(cls, v):
        if v < 2020 or v > 2050:
            raise ValueError('El año debe estar entre 2020 y 2050')
        return v
    
    class Config:
        from_attributes = True


class MesFlujCreate(MesFlujBase):
    """Schema para crear un nuevo mes de flujo"""
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "mes": 1,
                "anio": 2025,
                "saldo_inicial": 50000000.00,
                "observaciones": "Inicio del año fiscal 2025"
            }
        }


class MesFlujUpdate(BaseModel):
    """Schema para actualizar un mes de flujo"""
    saldo_inicial: Optional[Decimal] = None
    observaciones: Optional[str] = None
    archivo_excel_original: Optional[str] = None
    
    class Config:
        from_attributes = True


class MesFlujResponse(MesFlujBase):
    """Schema para la respuesta de MesFlujo"""
    id: int
    saldo_final: Optional[Decimal]
    esta_cerrado: bool
    fecha_cierre: Optional[datetime]
    cerrado_por: Optional[int]
    total_ingresos: Decimal
    total_egresos: Decimal
    flujo_neto: Decimal
    archivo_excel_original: Optional[str]
    creado_en: datetime
    actualizado_en: Optional[datetime]
    
    # Campos calculados
    nombre_mes: str = ""
    periodo_completo: str = ""
    fecha_inicio: date = None
    fecha_fin: date = None
    dias_mes: int = 0
    
    class Config:
        from_attributes = True


class MesFlujList(BaseModel):
    """Schema para listado de meses de flujo"""
    meses: List[MesFlujResponse]
    total: int
    anio_actual: int
    
    class Config:
        from_attributes = True


class ResumenAnual(BaseModel):
    """Schema para resumen anual de flujo de caja"""
    anio: int
    meses: List[MesFlujResponse]
    total_ingresos_anual: Decimal
    total_egresos_anual: Decimal
    flujo_neto_anual: Decimal
    saldo_inicial_anual: Decimal
    saldo_final_anual: Decimal
    promedio_mensual_ingresos: Decimal
    promedio_mensual_egresos: Decimal
    mes_mayor_ingreso: Optional[str]
    mes_mayor_egreso: Optional[str]
    
    class Config:
        from_attributes = True
