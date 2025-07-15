"""
Modelo Usuario - Gestión de usuarios del sistema con roles diferenciados
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class RolUsuario(str, enum.Enum):
    """Enum para los roles de usuario en el sistema"""
    TESORERIA = "tesoreria"
    PAGADURIA = "pagaduria" 
    MESA_DINERO = "mesa_dinero"


class Usuario(Base):
    """
    Modelo de Usuario del sistema
    
    Roles y permisos:
    - TESORERIA: Acceso completo, puede ver/editar todo
    - PAGADURIA: Solo egresos (nómina, proveedores)
    - MESA_DINERO: Solo consulta y reportes
    """
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False, default=RolUsuario.MESA_DINERO)
    
    # Estado y configuración
    esta_activo = Column(Boolean, default=True)
    primer_login = Column(Boolean, default=True)
    ultimo_acceso = Column(DateTime(timezone=True), nullable=True)
    
    # Metadatos
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    creado_por = Column(Integer, nullable=True)  # ID del usuario que lo creó
    
    # Configuración personalizada
    preferencias = Column(String(500), nullable=True)  # JSON con preferencias del usuario
    
    # Relaciones
    transacciones = relationship("Transaccion", back_populates="usuario", lazy="dynamic")
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre='{self.nombre}', rol='{self.rol.value}')>"
    
    @property
    def es_tesoreria(self) -> bool:
        """Verifica si el usuario tiene rol de tesorería"""
        return self.rol == RolUsuario.TESORERIA
    
    @property 
    def es_pagaduria(self) -> bool:
        """Verifica si el usuario tiene rol de pagaduría"""
        return self.rol == RolUsuario.PAGADURIA
        
    @property
    def es_mesa_dinero(self) -> bool:
        """Verifica si el usuario tiene rol de mesa de dinero"""
        return self.rol == RolUsuario.MESA_DINERO
    
    def puede_ver_transaccion(self, tipo_transaccion: str) -> bool:
        """
        Verifica si el usuario puede ver un tipo específico de transacción
        """
        if self.es_tesoreria:
            return True
        elif self.es_pagaduria:
            return tipo_transaccion in ["egreso", "nomina", "proveedores"]
        else:  # mesa_dinero
            return True  # Puede ver todo pero no editar
    
    def puede_editar_transaccion(self, tipo_transaccion: str) -> bool:
        """
        Verifica si el usuario puede editar un tipo específico de transacción
        """
        if self.es_tesoreria:
            return True
        elif self.es_pagaduria:
            return tipo_transaccion in ["egreso", "nomina", "proveedores"] 
        else:  # mesa_dinero
            return False  # Solo lectura
