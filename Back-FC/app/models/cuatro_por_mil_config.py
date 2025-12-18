"""
Modelo para la configuración de Cuatro por Mil por cuenta bancaria (Pagaduría)
Sistema de versionado: cada cambio crea un nuevo registro con fecha_vigencia_desde
Similar a GMFConfig pero para el área de Pagaduría
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CuatroPorMilConfig(Base):
    """Configuración Cuatro por Mil por cuenta bancaria con versionado histórico
    
    Cada modificación crea un nuevo registro con fecha_vigencia_desde.
    La config aplicable para un día X es la más reciente con fecha_vigencia_desde <= X
    
    Conceptos base permitidos (Pagaduría - todos son egresos):
    - ID 68: EMBARGOS
    - ID 69: OTROS PAGOS
    - ID 76: PAGO SOI
    - ID 78: OTROS IMPTOS
    
    Fórmula: CUATRO_POR_MIL = SUM(conceptos_seleccionados) × 4/1000
    """
    __tablename__ = "cuatro_por_mil_config"
    
    id = Column(Integer, primary_key=True, index=True)
    cuenta_bancaria_id = Column(Integer, ForeignKey("cuentas_bancarias.id"), nullable=False)
    conceptos_seleccionados = Column(Text, nullable=True)  # JSON string con los IDs de conceptos seleccionados
    activo = Column(Boolean, default=True)  # Para soft-delete de versiones anteriores
    fecha_vigencia_desde = Column(Date, nullable=False, index=True)  # Desde qué día aplica esta config
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())  # Cuándo se creó el registro
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    cuenta_bancaria = relationship("CuentaBancaria", back_populates="cuatro_por_mil_configs")
    
    def __repr__(self):
        return f"<CuatroPorMilConfig(id={self.id}, cuenta={self.cuenta_bancaria_id}, vigencia_desde={self.fecha_vigencia_desde})>"
