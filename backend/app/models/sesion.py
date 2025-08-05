from sqlalchemy import Column, Integer, String, Text, DATETIME, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel
import enum

class EstadoSesion(str, enum.Enum):
    ACTIVA = "ACTIVA"
    CERRADA = "CERRADA"
    EXPIRADA = "EXPIRADA"

class SesionUsuario(BaseModel):
    __tablename__ = "sesion_usuario"
    
    id_sesion = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    token_session = Column(String(255))
    inicio_sesion = Column(DATETIME, server_default=func.current_timestamp())
    fin_sesion = Column(DATETIME, nullable=True)
    ip = Column(String(45))
    user_agent = Column(Text)
    estado = Column(SQLEnum(EstadoSesion), default=EstadoSesion.ACTIVA)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="sesiones")
