from sqlalchemy import Column, Integer, String, Boolean
from ..core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False)  # administrador, tesoreria, pagaduria, mesa_dinero
    estado = Column(Boolean, nullable=False, default=True)  # True = activo, False = inactivo
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre='{self.nombre}', email='{self.email}', rol='{self.rol}', estado={self.estado}')>"