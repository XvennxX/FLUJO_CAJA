from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class TipoMovimiento(enum.Enum):
    ingreso = "ingreso"
    egreso = "egreso"
    neutral = "neutral"

class AreaConcepto(enum.Enum):
    tesoreria = "tesoreria"
    pagaduria = "pagaduria"
    ambas = "ambas"

class TipoDependencia(enum.Enum):
    copia = "copia"
    suma = "suma"
    resta = "resta"

class ConceptoFlujoCaja(Base):
    __tablename__ = "conceptos_flujo_caja"
    
    # Campos básicos
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(10), nullable=True)  # I, E, vacio
    tipo = Column(Enum(TipoMovimiento), nullable=False)
    
    # Configuración de área y visualización
    area = Column(Enum(AreaConcepto), nullable=False, default=AreaConcepto.ambas)
    orden_display = Column(Integer, default=0, index=True)
    activo = Column(Boolean, default=True, index=True)
    
    # Sistema de dependencias automáticas
    depende_de_concepto_id = Column(Integer, ForeignKey("conceptos_flujo_caja.id", ondelete="SET NULL"), nullable=True)
    tipo_dependencia = Column(Enum(TipoDependencia), nullable=True)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    transacciones = relationship("TransaccionFlujoCaja", back_populates="concepto")
    
    # Auto-referencia para dependencias
    concepto_dependiente = relationship("ConceptoFlujoCaja", remote_side=[id], backref="conceptos_dependientes")
    
    def __repr__(self):
        return f"<ConceptoFlujoCaja(id={self.id}, nombre='{self.nombre}', area='{self.area}', tipo='{self.tipo}')>"