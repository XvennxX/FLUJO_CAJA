from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuario"
    
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String(100))
    correo = Column(String(100), unique=True)
    contraseña = Column(String(255))
    id_rol = Column(Integer, ForeignKey("rol.id_rol"))
    estado = Column(Boolean, default=True)
    
    # Relaciones
    rol = relationship("Rol", back_populates="usuarios")
