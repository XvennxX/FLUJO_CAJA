from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..core.database import Base

class Banco(Base):
    __tablename__ = "bancos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    
    # Relaciones
    cuentas_bancarias = relationship("CuentaBancaria", back_populates="banco")
    
    def __repr__(self):
        return f"<Banco(id={self.id}, nombre='{self.nombre}')>"