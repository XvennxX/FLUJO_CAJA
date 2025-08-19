from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class TipoMoneda(enum.Enum):
    COP = "COP"
    USD = "USD"
    EUR = "EUR"
    OTRO = "OTRO"

class CuentaBancaria(Base):
    __tablename__ = "cuentas_bancarias"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    numero_cuenta = Column(String(50), nullable=False)
    compania_id = Column(Integer, ForeignKey("companias.id"), nullable=False)
    banco_id = Column(Integer, ForeignKey("bancos.id"), nullable=False)
    moneda = Column(Enum(TipoMoneda), nullable=False, default=TipoMoneda.COP)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    compania = relationship("Compania", back_populates="cuentas_bancarias")
    banco = relationship("Banco", back_populates="cuentas_bancarias")
    transacciones = relationship("TransaccionFlujoCaja", back_populates="cuenta")
    
    def __repr__(self):
        return f"<CuentaBancaria(id={self.id}, numero='{self.numero_cuenta}', moneda='{self.moneda}')>"