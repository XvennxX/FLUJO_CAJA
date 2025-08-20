from sqlalchemy import Column, Integer, String, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class TipoMoneda(enum.Enum):
    COP = "COP"
    USD = "USD"
    EUR = "EUR"

class CuentaMoneda(Base):
    __tablename__ = "cuenta_moneda"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_cuenta = Column(Integer, ForeignKey("cuentas_bancarias.id", ondelete="CASCADE"), nullable=False)
    moneda = Column(Enum(TipoMoneda), nullable=False)
    
    # Relaciones
    cuenta = relationship("CuentaBancaria", back_populates="monedas")
    
    # Constraint para evitar duplicados de cuenta-moneda
    __table_args__ = (
        UniqueConstraint('id_cuenta', 'moneda', name='unique_cuenta_moneda'),
    )
    
    def __repr__(self):
        return f"<CuentaMoneda(id={self.id}, cuenta_id={self.id_cuenta}, moneda='{self.moneda}')>"
