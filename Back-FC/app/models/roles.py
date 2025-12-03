"""
Modelos para sistema de Roles y Permisos (RBAC)
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

# Tabla intermedia para Many-to-Many entre Roles y Permisos
rol_permiso = Table(
    'rol_permiso',
    Base.metadata,
    Column('rol_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permiso_id', Integer, ForeignKey('permisos.id', ondelete='CASCADE'), primary_key=True)
)

class Rol(Base):
    """
    Modelo para roles del sistema.
    Un rol agrupa un conjunto de permisos.
    """
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)  # Identificador único (ej: 'ADMIN', 'TESORERIA')
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    es_sistema = Column(Boolean, default=False, nullable=False)  # True = no se puede eliminar
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relaciones
    permisos = relationship('Permiso', secondary=rol_permiso, back_populates='roles')
    usuarios = relationship('Usuario', back_populates='rol_obj')
    
    def __repr__(self):
        return f"<Rol(id={self.id}, nombre='{self.nombre}', codigo='{self.codigo}')>"
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "activo": self.activo,
            "es_sistema": self.es_sistema,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            "permisos": [p.to_dict() for p in self.permisos] if self.permisos else []
        }


class Permiso(Base):
    """
    Modelo para permisos del sistema.
    Un permiso representa una acción específica que se puede realizar.
    """
    __tablename__ = "permisos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(100), unique=True, nullable=False, index=True)  # Ej: 'transacciones.crear', 'usuarios.editar'
    descripcion = Column(Text, nullable=True)
    modulo = Column(String(50), nullable=False, index=True)  # Módulo al que pertenece (ej: 'transacciones', 'usuarios', 'reportes')
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relaciones
    roles = relationship('Rol', secondary=rol_permiso, back_populates='permisos')
    
    def __repr__(self):
        return f"<Permiso(id={self.id}, codigo='{self.codigo}', modulo='{self.modulo}')>"
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "modulo": self.modulo,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
