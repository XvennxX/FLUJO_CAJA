from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Banco(Base):
    __tablename__ = "bancos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    cuentas_bancarias = relationship("CuentaBancaria", back_populates="banco")
    
    def __repr__(self):
        return f"<Banco(id={self.id}, nombre='{self.nombre}')>"