"""
Schemas Pydantic para Roles y Permisos
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== PERMISOS ==========

class PermisoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre descriptivo del permiso")
    codigo: str = Field(..., min_length=1, max_length=100, description="Código único del permiso (ej: transacciones.crear)")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del permiso")
    modulo: str = Field(..., min_length=1, max_length=50, description="Módulo al que pertenece el permiso")
    activo: bool = Field(True, description="Si el permiso está activo")


class PermisoCreate(PermisoBase):
    """Schema para crear un permiso"""
    pass


class PermisoUpdate(BaseModel):
    """Schema para actualizar un permiso"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    modulo: Optional[str] = Field(None, min_length=1, max_length=50)
    activo: Optional[bool] = None


class PermisoResponse(PermisoBase):
    """Schema de respuesta de un permiso"""
    id: int
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


# ========== ROLES ==========

class RolBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50, description="Nombre del rol")
    codigo: str = Field(..., min_length=1, max_length=50, description="Código único del rol (ej: ADMIN, TESORERIA)")
    descripcion: Optional[str] = Field(None, description="Descripción del rol")
    activo: bool = Field(True, description="Si el rol está activo")


class RolCreate(RolBase):
    """Schema para crear un rol"""
    permisos_ids: List[int] = Field(default_factory=list, description="IDs de los permisos asignados al rol")


class RolUpdate(BaseModel):
    """Schema para actualizar un rol"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    permisos_ids: Optional[List[int]] = Field(None, description="IDs de los permisos asignados al rol")


class RolResponse(RolBase):
    """Schema de respuesta de un rol"""
    id: int
    es_sistema: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    permisos: List[PermisoResponse] = []
    
    class Config:
        from_attributes = True


class RolSimple(BaseModel):
    """Schema simplificado de un rol (para listados)"""
    id: int
    nombre: str
    codigo: str
    activo: bool
    es_sistema: bool
    cant_permisos: int = 0
    
    class Config:
        from_attributes = True


# ========== ASIGNACIÓN DE PERMISOS A ROLES ==========

class AsignarPermisosRequest(BaseModel):
    """Schema para asignar permisos a un rol"""
    permisos_ids: List[int] = Field(..., description="Lista de IDs de permisos a asignar")


class RemoverPermisosRequest(BaseModel):
    """Schema para remover permisos de un rol"""
    permisos_ids: List[int] = Field(..., description="Lista de IDs de permisos a remover")


# ========== LISTADOS Y AGRUPACIONES ==========

class PermisosPorModulo(BaseModel):
    """Schema para agrupar permisos por módulo"""
    modulo: str
    permisos: List[PermisoResponse]


class RolConEstadisticas(RolResponse):
    """Schema de rol con estadísticas adicionales"""
    cantidad_usuarios: int = 0
    cantidad_permisos: int = 0
