"""
Schemas Pydantic para el sistema de flujo de caja
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

# Enums
class TipoMovimientoSchema(str, Enum):
    ingreso = "ingreso"
    egreso = "egreso"
    neutral = "neutral"

class AreaConceptoSchema(str, Enum):
    tesoreria = "tesoreria"
    pagaduria = "pagaduria"
    ambas = "ambas"

class TipoDependenciaSchema(str, Enum):
    copia = "copia"
    suma = "suma"
    resta = "resta"

class AreaTransaccionSchema(str, Enum):
    tesoreria = "tesoreria"
    pagaduria = "pagaduria"

# ============================================
# SCHEMAS PARA CONCEPTOS DE FLUJO DE CAJA
# ============================================

class ConceptoFlujoCajaBase(BaseModel):
    nombre: str = Field(..., max_length=100, description="Nombre del concepto")
    codigo: Optional[str] = Field(None, max_length=10, description="Código del dashboard (I, E, vacío)")
    tipo: TipoMovimientoSchema = Field(..., description="Tipo de movimiento")
    area: AreaConceptoSchema = Field(AreaConceptoSchema.ambas, description="Área donde aparece")
    orden_display: int = Field(0, description="Orden en el dashboard")
    activo: bool = Field(True, description="Si está activo para usar")
    
    class Config:
        from_attributes = True

class ConceptoFlujoCajaCreate(ConceptoFlujoCajaBase):
    """Schema para crear conceptos"""
    depende_de_concepto_id: Optional[int] = Field(None, description="ID del concepto del cual depende")
    tipo_dependencia: Optional[TipoDependenciaSchema] = Field(None, description="Tipo de dependencia")
    
    @validator('tipo_dependencia')
    def validar_dependencia(cls, v, values):
        """Validar que si hay dependencia, debe tener tipo"""
        depende_de = values.get('depende_de_concepto_id')
        if depende_de is not None and v is None:
            raise ValueError('Si especifica depende_de_concepto_id, debe especificar tipo_dependencia')
        if depende_de is None and v is not None:
            raise ValueError('Si especifica tipo_dependencia, debe especificar depende_de_concepto_id')
        return v

class ConceptoFlujoCajaUpdate(BaseModel):
    """Schema para actualizar conceptos"""
    nombre: Optional[str] = Field(None, max_length=100)
    codigo: Optional[str] = Field(None, max_length=10)
    tipo: Optional[TipoMovimientoSchema] = None
    area: Optional[AreaConceptoSchema] = None
    orden_display: Optional[int] = None
    activo: Optional[bool] = None
    depende_de_concepto_id: Optional[int] = None
    tipo_dependencia: Optional[TipoDependenciaSchema] = None
    
    class Config:
        from_attributes = True

class ConceptoFlujoCajaResponse(ConceptoFlujoCajaBase):
    """Schema para respuesta de conceptos"""
    id: int
    depende_de_concepto_id: Optional[int] = None
    tipo_dependencia: Optional[TipoDependenciaSchema] = None
    created_at: datetime
    updated_at: datetime
    
    # Información de dependencia (si aplica)
    concepto_dependiente: Optional['ConceptoFlujoCajaResponse'] = None
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA TRANSACCIONES DE FLUJO DE CAJA
# ============================================

class TransaccionFlujoCajaBase(BaseModel):
    fecha: date = Field(..., description="Fecha de la transacción")
    concepto_id: int = Field(..., description="ID del concepto")
    cuenta_id: Optional[int] = Field(None, description="ID de la cuenta bancaria")
    monto: Decimal = Field(..., ge=0, description="Monto de la transacción")
    descripcion: Optional[str] = Field(None, description="Descripción adicional")
    area: AreaTransaccionSchema = Field(AreaTransaccionSchema.tesoreria, description="Área de la transacción")
    compania_id: Optional[int] = Field(None, description="ID de la compañía")
    
    class Config:
        from_attributes = True

class TransaccionFlujoCajaCreate(TransaccionFlujoCajaBase):
    """Schema para crear transacciones"""
    pass

class TransaccionFlujoCajaUpdate(BaseModel):
    """Schema para actualizar transacciones"""
    fecha: Optional[date] = None
    concepto_id: Optional[int] = None
    cuenta_id: Optional[int] = None
    monto: Optional[Decimal] = Field(None, ge=0)
    descripcion: Optional[str] = None
    area: Optional[AreaTransaccionSchema] = None
    compania_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class TransaccionFlujoCajaResponse(TransaccionFlujoCajaBase):
    """Schema para respuesta de transacciones"""
    id: int
    usuario_id: Optional[int] = None
    auditoria: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    # Información relacionada
    concepto: Optional[ConceptoFlujoCajaResponse] = None
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA REPORTES Y DASHBOARDS
# ============================================

class FlujoCajaDiarioItem(BaseModel):
    """Item individual del flujo de caja diario"""
    concepto_id: int
    concepto_nombre: str
    concepto_codigo: Optional[str]
    concepto_tipo: TipoMovimientoSchema
    orden_display: int
    monto: Decimal = Field(default=Decimal('0.00'))
    
    class Config:
        from_attributes = True

class FlujoCajaDiarioResponse(BaseModel):
    """Respuesta completa del flujo de caja diario"""
    fecha: date
    area: AreaConceptoSchema
    conceptos: List[FlujoCajaDiarioItem]
    totales: Dict[str, Decimal] = Field(default_factory=dict)  # totales por tipo
    
    class Config:
        from_attributes = True

class FlujoCajaResumenResponse(BaseModel):
    """Resumen del flujo de caja"""
    fecha_inicio: date
    fecha_fin: date
    area: AreaConceptoSchema
    total_ingresos: Decimal
    total_egresos: Decimal
    saldo_neto: Decimal
    transacciones_count: int
    
    class Config:
        from_attributes = True

# Permitir referencias forward
ConceptoFlujoCajaResponse.model_rebuild()
