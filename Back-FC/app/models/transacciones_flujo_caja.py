from sqlalchemy import Column, Integer, String, ForeignKey, Date, DECIMAL, Text
from sqlalchemy.orm import relationship
from ..core.database import Base

class TransaccionFlujoCaja(Base):
    __tablename__ = "transacciones_flujo_caja"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date, nullable=False, index=True)
    concepto_id = Column(Integer, ForeignKey("conceptos_flujo_caja.id"), nullable=False)
    cuenta_id = Column(Integer, ForeignKey("cuentas_bancarias.id"), nullable=False)
    monto = Column(DECIMAL(15, 2), nullable=False)
    descripcion = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Relaciones
    concepto = relationship("ConceptoFlujoCaja", back_populates="transacciones")
    cuenta = relationship("CuentaBancaria", back_populates="transacciones")
    usuario = relationship("Usuario")
    
    def __repr__(self):
        return f"<TransaccionFlujoCaja(id={self.id}, fecha='{self.fecha}', monto={self.monto})>"