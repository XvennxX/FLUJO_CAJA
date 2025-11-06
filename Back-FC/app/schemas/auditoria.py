from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AccionAuditoria(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE" 
    DELETE = "DELETE"
    READ = "READ"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"

class ModuloAuditoria(str, Enum):
    FLUJO_CAJA = "FLUJO_CAJA"
    EMPRESAS = "EMPRESAS"
    CUENTAS = "CUENTAS"
    REPORTES = "REPORTES"
    USUARIOS = "USUARIOS"
    CONCEPTOS = "CONCEPTOS"
    SISTEMA = "SISTEMA"

class ResultadoAuditoria(str, Enum):
    EXITOSO = "EXITOSO"
    ERROR = "ERROR"
    ADVERTENCIA = "ADVERTENCIA"

# Schemas para respuestas
class RegistroAuditoriaResponse(BaseModel):
    id: int
    usuario_id: int
    usuario_nombre: str
    usuario_email: str
    accion: str
    modulo: str
    entidad: str
    entidad_id: Optional[str] = None
    descripcion: str
    valores_anteriores: Optional[Dict[str, Any]] = None
    valores_nuevos: Optional[Dict[str, Any]] = None
    ip_address: str
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    metodo_http: Optional[str] = None
    fecha_hora: datetime
    duracion_ms: Optional[int] = None
    resultado: str
    mensaje_error: Optional[str] = None

    class Config:
        from_attributes = True

class AuditoriaListResponse(BaseModel):
    registros: List[RegistroAuditoriaResponse]
    total: int
    pagina: int
    limite: int
    total_paginas: int

# Schemas para requests/filtros
class FiltrosAuditoria(BaseModel):
    usuario_id: Optional[int] = None
    accion: Optional[str] = None
    modulo: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    busqueda: Optional[str] = None
    pagina: int = Field(1, ge=1)
    limite: int = Field(50, ge=1, le=1000)

# Schema para estadísticas
class EstadisticaItem(BaseModel):
    nombre: str
    total: int

class EstadisticasAuditoria(BaseModel):
    total_registros: int
    registros_hoy: int
    registros_semana: int
    registros_mes: int
    acciones: List[EstadisticaItem]
    modulos: List[EstadisticaItem]
    usuarios_activos: List[EstadisticaItem]
    ips_frecuentes: List[EstadisticaItem]

# Schema para crear registro manual (administradores)
class CrearRegistroAuditoria(BaseModel):
    accion: AccionAuditoria
    modulo: ModuloAuditoria
    entidad: str = Field(..., min_length=1, max_length=100)
    entidad_id: Optional[str] = Field(None, max_length=50)
    descripcion: str = Field(..., min_length=1, max_length=500)
    valores_anteriores: Optional[Dict[str, Any]] = None
    valores_nuevos: Optional[Dict[str, Any]] = None
    resultado: ResultadoAuditoria = ResultadoAuditoria.EXITOSO
    mensaje_error: Optional[str] = None

# Schema para exportar auditoría
class ExportarAuditoriaRequest(BaseModel):
    formato: str = Field("excel", pattern="^(excel|csv|pdf)$")
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    usuario_id: Optional[int] = None
    accion: Optional[str] = None
    modulo: Optional[str] = None
    incluir_valores: bool = False  # Si incluir valores anteriores/nuevos

# Schemas para dashboards específicos
class AuditoriaUsuario(BaseModel):
    usuario_nombre: str
    total_acciones: int
    ultima_actividad: datetime
    acciones_por_tipo: Dict[str, int]
    modulos_utilizados: List[str]

class AuditoriaPorFecha(BaseModel):
    fecha: datetime
    total_acciones: int
    acciones_exitosas: int
    acciones_error: int
    usuarios_activos: int

class ResumenDiarioAuditoria(BaseModel):
    fecha: datetime
    total_transacciones: int
    modificaciones_flujo_caja: int
    exportaciones: int
    usuarios_activos: int
    errores_detectados: int
    ip_addresses_unicas: int