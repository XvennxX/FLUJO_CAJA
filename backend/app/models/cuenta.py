from sqlalchemy import Column, Integer, String, Boolean, DECIMAL
from sqlalchemy.orm import relationship
from app.core.database import Base

class Cuenta(Base):
    __tablename__ = "cuenta"
    
    id_cuenta = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    saldo_actual = Column(DECIMAL(12, 2), default=0.00)
    estado = Column(Boolean, default=True)
    
    # Relaciones
    ingresos = relationship("Ingreso", back_populates="cuenta")
    egresos = relationship("Egreso", back_populates="cuenta")
