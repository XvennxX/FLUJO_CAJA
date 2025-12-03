"""
Modelo para la configuración de GMF por cuenta bancaria
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class GMFConfig(Base):
    """Configuración GMF por cuenta bancaria"""
    __tablename__ = "gmf_config"
    
    id = Column(Integer, primary_key=True, index=True)
    cuenta_bancaria_id = Column(Integer, ForeignKey("cuentas_bancarias.id"), nullable=False)
    conceptos_seleccionados = Column(Text, nullable=True)  # JSON string con los conceptos seleccionados
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    cuenta_bancaria = relationship("CuentaBancaria", back_populates="gmf_configs")
    
    def __repr__(self):
        return f"<GMFConfig(id={self.id}, cuenta_bancaria_id={self.cuenta_bancaria_id})>"