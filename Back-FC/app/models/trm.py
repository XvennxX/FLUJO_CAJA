from sqlalchemy import Column, Date, DECIMAL, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from app.core.database import Base

class TRM(Base):
    __tablename__ = "trm"
    
    fecha = Column(Date, primary_key=True, comment="Fecha de la TRM")
    valor = Column(DECIMAL(18, 6), nullable=False, comment="Valor de la TRM")
    fecha_creacion = Column(TIMESTAMP, default=func.current_timestamp(), comment="Fecha de creación del registro")
    
    def __repr__(self):
        return f"<TRM(fecha={self.fecha}, valor={self.valor})>"
