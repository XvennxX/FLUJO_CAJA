from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta, timezone
import json
from fastapi import Request
import time

from ..models.auditoria import RegistroAuditoria
from ..models.usuarios import Usuario
from ..core.database import get_db

# Zona horaria de Colombia (UTC-5)
COLOMBIA_TZ = timezone(timedelta(hours=-5))

def obtener_hora_colombia() -> datetime:
    """Obtiene la hora actual en zona horaria de Colombia (UTC-5)"""
    return datetime.now(COLOMBIA_TZ)

class AuditoriaService:
    """Servicio para manejar el registro de auditoría del sistema"""
    
    @staticmethod
    def registrar_accion(
        db: Session,
        usuario: Usuario,
        accion: str,
        modulo: str,
        entidad: str,
        descripcion: str,
        request: Request = None,
        entidad_id: str = None,
        valores_anteriores: Dict[str, Any] = None,
        valores_nuevos: Dict[str, Any] = None,
        endpoint: str = None,
        metodo_http: str = None,
        duracion_ms: int = None,
        resultado: str = "EXITOSO",
        mensaje_error: str = None
    ) -> RegistroAuditoria:
        """Registra una acción de auditoría en la base de datos"""
        
        # Obtener IP del cliente
        ip_address = "127.0.0.1"
        user_agent = None
        
        if request:
            # Intentar obtener la IP real del cliente
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                ip_address = forwarded_for.split(",")[0].strip()
            else:
                ip_address = getattr(request.client, 'host', '127.0.0.1')
            
            user_agent = request.headers.get("User-Agent")
            
            if not endpoint:
                endpoint = str(request.url.path)
            if not metodo_http:
                metodo_http = request.method

        # Crear registro de auditoría
        registro = RegistroAuditoria(
            usuario_id=usuario.id,
            usuario_nombre=usuario.nombre,
            usuario_email=usuario.email,
            accion=accion.upper(),
            modulo=modulo.upper(),
            entidad=entidad,
            entidad_id=entidad_id,
            descripcion=descripcion,
            valores_anteriores=valores_anteriores,
            valores_nuevos=valores_nuevos,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            metodo_http=metodo_http,
            fecha_hora=obtener_hora_colombia(),
            duracion_ms=duracion_ms,
            resultado=resultado.upper(),
            mensaje_error=mensaje_error
        )
        
        db.add(registro)
        db.commit()
        db.refresh(registro)
        
        return registro

    @staticmethod
    def obtener_registros(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        usuario_id: int = None,
        accion: str = None,
        modulo: str = None,
        fecha_inicio: datetime = None,
        fecha_fin: datetime = None,
        busqueda: str = None
    ) -> tuple[List[RegistroAuditoria], int]:
        """Obtiene registros de auditoría con filtros opcionales"""
        
        query = db.query(RegistroAuditoria)
        
        # Filtros
        if usuario_id:
            query = query.filter(RegistroAuditoria.usuario_id == usuario_id)
        
        if accion and accion.upper() != "TODAS":
            query = query.filter(RegistroAuditoria.accion == accion.upper())
        
        if modulo and modulo.upper() != "TODOS":
            query = query.filter(RegistroAuditoria.modulo == modulo.upper())
        
        if fecha_inicio and fecha_fin:
            query = query.filter(and_(
                RegistroAuditoria.fecha_hora >= fecha_inicio,
                RegistroAuditoria.fecha_hora <= fecha_fin
            ))
        
        if busqueda:
            search_filter = or_(
                RegistroAuditoria.descripcion.ilike(f"%{busqueda}%"),
                RegistroAuditoria.usuario_nombre.ilike(f"%{busqueda}%"),
                RegistroAuditoria.entidad.ilike(f"%{busqueda}%")
            )
            query = query.filter(search_filter)
        
        # Contar total
        total = query.count()
        
        # Ordenar por fecha descendente y paginar
        registros = query.order_by(desc(RegistroAuditoria.fecha_hora)).offset(skip).limit(limit).all()
        
        return registros, total

    @staticmethod
    def obtener_estadisticas(
        db: Session,
        fecha_inicio: datetime = None,
        fecha_fin: datetime = None
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de auditoría"""
        
        query = db.query(RegistroAuditoria)
        
        if fecha_inicio and fecha_fin:
            query = query.filter(and_(
                RegistroAuditoria.fecha_hora >= fecha_inicio,
                RegistroAuditoria.fecha_hora <= fecha_fin
            ))
        
        # Estadísticas por acción
        acciones = db.query(
            RegistroAuditoria.accion,
            func.count(RegistroAuditoria.id).label('total')
        ).group_by(RegistroAuditoria.accion).all()
        
        # Estadísticas por módulo
        modulos = db.query(
            RegistroAuditoria.modulo,
            func.count(RegistroAuditoria.id).label('total')
        ).group_by(RegistroAuditoria.modulo).all()
        
        # Estadísticas por usuario
        usuarios = db.query(
            RegistroAuditoria.usuario_nombre,
            func.count(RegistroAuditoria.id).label('total')
        ).group_by(RegistroAuditoria.usuario_nombre).order_by(desc('total')).limit(10).all()
        
        # Total de registros
        total_registros = query.count()
        
        return {
            "total_registros": total_registros,
            "acciones": [{"accion": a.accion, "total": a.total} for a in acciones],
            "modulos": [{"modulo": m.modulo, "total": m.total} for m in modulos],
            "usuarios_activos": [{"usuario": u.usuario_nombre, "total": u.total} for u in usuarios]
        }

    @staticmethod
    def obtener_usuarios_activos(db: Session) -> List[dict]:
        """Obtiene lista de usuarios que han realizado acciones con ID y nombre"""
        usuarios = db.query(
            RegistroAuditoria.usuario_id,
            RegistroAuditoria.usuario_nombre
        ).distinct().all()
        return [{"id": u.usuario_id, "nombre": u.usuario_nombre} for u in usuarios]

# Funciones helper para logging específico de cada módulo

def log_transaccion_flujo_caja(
    db: Session,
    usuario: Usuario,
    accion: str,
    fecha: str,
    concepto: str,
    cuenta: str,
    valor_anterior: float = None,
    valor_nuevo: float = None,
    request: Request = None
):
    """Log específico para transacciones de flujo de caja"""
    
    descripcion = f"{accion} transacción: {concepto} en {cuenta}"
    if valor_anterior is not None and valor_nuevo is not None:
        descripcion += f" (${valor_anterior:,.0f} → ${valor_nuevo:,.0f})"
    elif valor_nuevo is not None:
        descripcion += f" por ${valor_nuevo:,.0f}"
    
    valores_anteriores = {"valor": valor_anterior} if valor_anterior is not None else None
    valores_nuevos = {"valor": valor_nuevo} if valor_nuevo is not None else None
    
    return AuditoriaService.registrar_accion(
        db=db,
        usuario=usuario,
        accion=accion,
        modulo="FLUJO_CAJA",
        entidad="Transacción",
        entidad_id=fecha,
        descripcion=descripcion,
        valores_anteriores=valores_anteriores,
        valores_nuevos=valores_nuevos,
        request=request
    )

def log_gestion_empresa(
    db: Session,
    usuario: Usuario,
    accion: str,
    empresa_id: int,
    empresa_nombre: str,
    datos_anteriores: Dict = None,
    datos_nuevos: Dict = None,
    request: Request = None
):
    """Log específico para gestión de empresas"""
    
    descripcion = f"{accion} empresa: {empresa_nombre}"
    
    return AuditoriaService.registrar_accion(
        db=db,
        usuario=usuario,
        accion=accion,
        modulo="EMPRESAS",
        entidad="Empresa",
        entidad_id=str(empresa_id),
        descripcion=descripcion,
        valores_anteriores=datos_anteriores,
        valores_nuevos=datos_nuevos,
        request=request
    )

def log_gestion_cuenta(
    db: Session,
    usuario: Usuario,
    accion: str,
    cuenta_id: int,
    numero_cuenta: str,
    banco: str,
    datos_anteriores: Dict = None,
    datos_nuevos: Dict = None,
    request: Request = None
):
    """Log específico para gestión de cuentas bancarias"""
    
    descripcion = f"{accion} cuenta: {numero_cuenta} ({banco})"
    
    return AuditoriaService.registrar_accion(
        db=db,
        usuario=usuario,
        accion=accion,
        modulo="CUENTAS",
        entidad="Cuenta Bancaria",
        entidad_id=str(cuenta_id),
        descripcion=descripcion,
        valores_anteriores=datos_anteriores,
        valores_nuevos=datos_nuevos,
        request=request
    )

def log_accion_usuario(
    db: Session,
    usuario_admin: Usuario,
    accion: str,
    usuario_afectado_id: int,
    usuario_afectado_nombre: str,
    datos_anteriores: Dict = None,
    datos_nuevos: Dict = None,
    request: Request = None
):
    """Log específico para gestión de usuarios"""
    
    descripcion = f"{accion} usuario: {usuario_afectado_nombre}"
    
    return AuditoriaService.registrar_accion(
        db=db,
        usuario=usuario_admin,
        accion=accion,
        modulo="USUARIOS",
        entidad="Usuario",
        entidad_id=str(usuario_afectado_id),
        descripcion=descripcion,
        valores_anteriores=datos_anteriores,
        valores_nuevos=datos_nuevos,
        request=request
    )

def log_reporte(
    db: Session,
    usuario: Usuario,
    tipo_reporte: str,
    parametros: Dict = None,
    request: Request = None
):
    """Log específico para generación de reportes"""
    
    descripcion = f"Generó reporte: {tipo_reporte}"
    if parametros:
        descripcion += f" con parámetros: {parametros}"
    
    return AuditoriaService.registrar_accion(
        db=db,
        usuario=usuario,
        accion="EXPORT",
        modulo="REPORTES",
        entidad="Reporte",
        descripcion=descripcion,
        valores_nuevos=parametros,
        request=request
    )