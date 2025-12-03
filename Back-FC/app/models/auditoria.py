from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from ..core.database import Base

# Zona horaria de Colombia (UTC-5)
COLOMBIA_TZ = timezone(timedelta(hours=-5))

def obtener_hora_colombia():
    """Obtiene la hora actual en zona horaria de Colombia (UTC-5)"""
    return datetime.now(COLOMBIA_TZ)

class RegistroAuditoria(Base):
    __tablename__ = "registros_auditoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False)
    usuario_nombre = Column(String(100), nullable=False)
    usuario_email = Column(String(255), nullable=False)
    accion = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, READ, EXPORT, IMPORT
    modulo = Column(String(50), nullable=False)  # FLUJO_CAJA, EMPRESAS, CUENTAS, REPORTES, USUARIOS, CONCEPTOS
    entidad = Column(String(100), nullable=False)  # Tipo de entidad afectada
    entidad_id = Column(String(50), nullable=True)  # ID de la entidad afectada
    descripcion = Column(Text, nullable=False)  # Descripción de la acción
    valores_anteriores = Column(JSON, nullable=True)  # Estado anterior (para updates/deletes)
    valores_nuevos = Column(JSON, nullable=True)  # Estado nuevo (para creates/updates)
    ip_address = Column(String(45), nullable=False)  # IPv4 o IPv6
    user_agent = Column(Text, nullable=True)  # Información del navegador
    endpoint = Column(String(255), nullable=True)  # Endpoint de la API llamado
    metodo_http = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    fecha_hora = Column(DateTime, default=obtener_hora_colombia, nullable=False)
    duracion_ms = Column(Integer, nullable=True)  # Duración de la operación en ms
    resultado = Column(String(20), nullable=False, default="EXITOSO")  # EXITOSO, ERROR, ADVERTENCIA
    mensaje_error = Column(Text, nullable=True)  # Mensaje de error si aplica
    sesion_id = Column(String(100), nullable=True)  # ID de la sesión
    
    def __repr__(self):
        return f"<RegistroAuditoria(id={self.id}, usuario={self.usuario_nombre}, accion={self.accion}, modulo={self.modulo})>"