from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class TipoConcepto(str, enum.Enum):
    INGRESO = "INGRESO"
    EGRESO = "EGRESO"

class Concepto(Base):
    __tablename__ = "concepto"
    
    id_concepto = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(SQLEnum(TipoConcepto), nullable=False)
    
    # Relaciones
    ingresos = relationship("Ingreso", back_populates="concepto")
    egresos = relationship("Egreso", back_populates="concepto")
