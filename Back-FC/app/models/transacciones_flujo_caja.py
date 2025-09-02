from sqlalchemy import Column, Integer, String, ForeignKey, Date, DECIMAL, Text, Boolean, DateTime, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class AreaTransaccion(enum.Enum):
    tesoreria = "tesoreria"
    pagaduria = "pagaduria"

class TransaccionFlujoCaja(Base):
    __tablename__ = "transacciones_flujo_caja"
    
    # Campos básicos
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date, nullable=False, index=True)
    concepto_id = Column(Integer, ForeignKey("conceptos_flujo_caja.id", ondelete="CASCADE"), nullable=False)
    cuenta_id = Column(Integer, ForeignKey("cuentas_bancarias.id", ondelete="CASCADE"), nullable=True)
    monto = Column(DECIMAL(18, 2), nullable=False, default=0.00)
    descripcion = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    
    # Configuración de área
    area = Column(Enum(AreaTransaccion), nullable=False, default=AreaTransaccion.tesoreria)
    compania_id = Column(Integer, ForeignKey("companias.id", ondelete="SET NULL"), nullable=True)
    
    # Campos de auditoría y automatización
    auditoria = Column(JSON, nullable=True)  # Info de auditoría (quién, cuándo, qué)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    concepto = relationship("ConceptoFlujoCaja", back_populates="transacciones")
    cuenta = relationship("CuentaBancaria", back_populates="transacciones")
    usuario = relationship("Usuario")
    compania = relationship("Compania")
    
    def __repr__(self):
        return f"<TransaccionFlujoCaja(id={self.id}, fecha='{self.fecha}', concepto='{self.concepto.nombre if self.concepto else 'N/A'}', monto={self.monto})>"