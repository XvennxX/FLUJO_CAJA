from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Compania(Base):
    __tablename__ = "companias"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    
    # Relaciones
    cuentas_bancarias = relationship("CuentaBancaria", back_populates="compania")
    transacciones_flujo_caja = relationship("TransaccionFlujoCaja", back_populates="compania")
    conciliaciones = relationship("ConciliacionContable", back_populates="empresa")
    
    def __repr__(self):
        return f"<Compania(id={self.id}, nombre='{self.nombre}')>"