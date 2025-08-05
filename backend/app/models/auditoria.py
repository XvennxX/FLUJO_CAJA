from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Auditoria(Base):
    __tablename__ = "auditoria"
    
    id_auditoria = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    accion = Column(String(255), nullable=False)
    fecha = Column(DateTime, server_default=func.current_timestamp())
    
    # Relaciones
    usuario = relationship("Usuario")
