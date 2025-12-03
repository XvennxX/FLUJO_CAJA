from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False)  # administrador, tesoreria, pagaduria, mesa_dinero (LEGACY - mantener por compatibilidad)
    rol_id = Column(Integer, ForeignKey('roles.id', ondelete='SET NULL'), nullable=True, index=True)  # Nuevo sistema de roles
    estado = Column(Boolean, nullable=False, default=True)  # True = activo, False = inactivo
    
    # Relaciones
    rol_obj = relationship('Rol', back_populates='usuarios', foreign_keys=[rol_id])
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre='{self.nombre}', email='{self.email}', rol='{self.rol}', estado={self.estado}')>"
    
    def tiene_permiso(self, codigo_permiso: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico a través de su rol.
        
        Args:
            codigo_permiso: Código del permiso a verificar (ej: 'transacciones.crear')
            
        Returns:
            bool: True si tiene el permiso, False si no
        """
        if not self.rol_obj or not self.rol_obj.activo:
            return False
        
        return any(
            p.codigo == codigo_permiso and p.activo 
            for p in self.rol_obj.permisos
        )
    
    def tiene_cualquier_permiso(self, codigos_permisos: list) -> bool:
        """
        Verifica si el usuario tiene al menos uno de los permisos especificados.
        
        Args:
            codigos_permisos: Lista de códigos de permisos
            
        Returns:
            bool: True si tiene al menos un permiso, False si no
        """
        return any(self.tiene_permiso(codigo) for codigo in codigos_permisos)
    
    def obtener_permisos(self) -> list:
        """
        Obtiene todos los permisos del usuario a través de su rol.
        
        Returns:
            list: Lista de códigos de permisos
        """
        if not self.rol_obj or not self.rol_obj.activo:
            return []
        
        return [p.codigo for p in self.rol_obj.permisos if p.activo]