from sqlalchemy import Column, Integer, ForeignKey, Date, DECIMAL, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Egreso(Base):
    __tablename__ = "egreso"
    
    id_egreso = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    valor = Column(DECIMAL(15, 2), nullable=False)
    observaciones = Column(String(255))
    id_concepto = Column(Integer, ForeignKey("concepto.id_concepto"), nullable=False)
    id_cuenta = Column(Integer, ForeignKey("cuenta.id_cuenta"), nullable=False)
    
    # Relaciones
    concepto = relationship("Concepto", back_populates="egresos")
    cuenta = relationship("Cuenta", back_populates="egresos")
