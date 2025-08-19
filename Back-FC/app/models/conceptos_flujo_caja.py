from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class TipoMovimiento(enum.Enum):
    ingreso = "ingreso"
    egreso = "egreso"
    neutral = "neutral"

class ConceptoFlujoCaja(Base):
    __tablename__ = "conceptos_flujo_caja"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoMovimiento), nullable=False)
    codigo = Column(String(50), nullable=True)  # Código para identificación (I, E, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    transacciones = relationship("TransaccionFlujoCaja", back_populates="concepto")
    
    def __repr__(self):
        return f"<ConceptoFlujoCaja(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo}')>"