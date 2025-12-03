from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date

from ..core.database import get_db
from ..services.auth_service import get_current_user, check_user_role
from ..services.auditoria_service import AuditoriaService
from ..models.usuarios import Usuario
from ..schemas.auditoria import (
    RegistroAuditoriaResponse,
    AuditoriaListResponse,
    FiltrosAuditoria,
    EstadisticasAuditoria,
    CrearRegistroAuditoria,
    ExportarAuditoriaRequest,
    AuditoriaUsuario,
    ResumenDiarioAuditoria
)

router = APIRouter(prefix="/auditoria", tags=["auditoria"])

@router.get("/registros", response_model=AuditoriaListResponse)
def obtener_registros_auditoria(
    pagina: int = Query(1, ge=1, description="Número de página"),
    limite: int = Query(50, ge=1, le=1000, description="Registros por página"),
    usuario_id: Optional[int] = Query(None, description="Filtrar por usuario"),
    accion: Optional[str] = Query(None, description="Filtrar por acción"),
    modulo: Optional[str] = Query(None, description="Filtrar por módulo"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    busqueda: Optional[str] = Query(None, description="Búsqueda en descripción, usuario o entidad"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador"]))
):
    """
    Obtener registros de auditoría con filtros opcionales.
    Solo disponible para administradores.
    """
    
    # Convertir fechas si se proporcionan
    fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time()) if fecha_inicio else None
    fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time()) if fecha_fin else None
    
    # Calcular offset
    skip = (pagina - 1) * limite
    
    # Obtener registros
    registros, total = AuditoriaService.obtener_registros(
        db=db,
        skip=skip,
        limit=limite,
        usuario_id=usuario_id,
        accion=accion,
        modulo=modulo,
        fecha_inicio=fecha_inicio_dt,
        fecha_fin=fecha_fin_dt,
        busqueda=busqueda
    )
    
    # Calcular total de páginas
    total_paginas = (total + limite - 1) // limite
    
    return AuditoriaListResponse(
        registros=registros,
        total=total,
        pagina=pagina,
        limite=limite,
        total_paginas=total_paginas
    )

@router.get("/estadisticas", response_model=EstadisticasAuditoria)
def obtener_estadisticas_auditoria(
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicio para estadísticas"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin para estadísticas"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador"]))
):
    """
    Obtener estadísticas de auditoría.
    Solo disponible para administradores.
    """
    
    # Si no se especifican fechas, usar últimos 30 días
    if not fecha_inicio:
        fecha_inicio = (datetime.now() - timedelta(days=30)).date()
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    
    fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time())
    fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time())
    
    estadisticas = AuditoriaService.obtener_estadisticas(
        db=db,
        fecha_inicio=fecha_inicio_dt,
        fecha_fin=fecha_fin_dt
    )
    
    # Obtener estadísticas adicionales
    hoy = datetime.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)
    
    _, registros_hoy = AuditoriaService.obtener_registros(
        db=db, 
        fecha_inicio=datetime.combine(hoy, datetime.min.time()),
        fecha_fin=datetime.combine(hoy, datetime.max.time())
    )
    
    _, registros_semana = AuditoriaService.obtener_registros(
        db=db,
        fecha_inicio=datetime.combine(inicio_semana, datetime.min.time())
    )
    
    _, registros_mes = AuditoriaService.obtener_registros(
        db=db,
        fecha_inicio=datetime.combine(inicio_mes, datetime.min.time())
    )
    
    return EstadisticasAuditoria(
        total_registros=estadisticas["total_registros"],
        registros_hoy=registros_hoy,
        registros_semana=registros_semana,
        registros_mes=registros_mes,
        acciones=[{"nombre": a["accion"], "total": a["total"]} for a in estadisticas["acciones"]],
        modulos=[{"nombre": m["modulo"], "total": m["total"]} for m in estadisticas["modulos"]],
        usuarios_activos=[{"nombre": u["usuario"], "total": u["total"]} for u in estadisticas["usuarios_activos"]],
        ips_frecuentes=[]  # Se puede implementar después
    )

@router.get("/usuarios-activos")
def obtener_usuarios_activos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador"]))
):
    """
    Obtener lista de usuarios que han realizado acciones de auditoría.
    """
    usuarios = AuditoriaService.obtener_usuarios_activos(db)
    return {"usuarios": usuarios}

@router.get("/registro/{registro_id}", response_model=RegistroAuditoriaResponse)
def obtener_detalle_registro(
    registro_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador"]))
):
    """
    Obtener detalle de un registro específico de auditoría.
    """
    from ..models.auditoria import RegistroAuditoria
    
    registro = db.query(RegistroAuditoria).filter(RegistroAuditoria.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de auditoría no encontrado")
    
    return registro

@router.post("/registro", response_model=RegistroAuditoriaResponse)
def crear_registro_manual(
    registro_data: CrearRegistroAuditoria,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador"]))
):
    """
    Crear un registro de auditoría manual.
    Solo para administradores en casos especiales.
    """
    
    registro = AuditoriaService.registrar_accion(
        db=db,
        usuario=current_user,
        accion=registro_data.accion,
        modulo=registro_data.modulo,
        entidad=registro_data.entidad,
        entidad_id=registro_data.entidad_id,
        descripcion=registro_data.descripcion,
        valores_anteriores=registro_data.valores_anteriores,
        valores_nuevos=registro_data.valores_nuevos,
        resultado=registro_data.resultado,
        mensaje_error=registro_data.mensaje_error,
        request=request
    )
    
    return registro

@router.get("/resumen-diario/{fecha}", response_model=ResumenDiarioAuditoria)
def obtener_resumen_diario(
    fecha: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador", "Tesorería", "tesoreria", "Pagaduría", "pagaduria"]))
):
    """
    Obtener resumen de auditoría para un día específico.
    """
    from sqlalchemy import func
    from ..models.auditoria import RegistroAuditoria
    
    fecha_inicio = datetime.combine(fecha, datetime.min.time())
    fecha_fin = datetime.combine(fecha, datetime.max.time())
    
    # Consultas para el resumen
    query_base = db.query(RegistroAuditoria).filter(
        RegistroAuditoria.fecha_hora >= fecha_inicio,
        RegistroAuditoria.fecha_hora <= fecha_fin
    )
    
    total_transacciones = query_base.count()
    
    modificaciones_flujo_caja = query_base.filter(
        RegistroAuditoria.modulo == "FLUJO_CAJA",
        RegistroAuditoria.accion.in_(["CREATE", "UPDATE"])
    ).count()
    
    exportaciones = query_base.filter(RegistroAuditoria.accion == "EXPORT").count()
    
    usuarios_activos = query_base.with_entities(RegistroAuditoria.usuario_id).distinct().count()
    
    errores_detectados = query_base.filter(RegistroAuditoria.resultado == "ERROR").count()
    
    ip_addresses_unicas = query_base.with_entities(RegistroAuditoria.ip_address).distinct().count()
    
    return ResumenDiarioAuditoria(
        fecha=datetime.combine(fecha, datetime.min.time()),
        total_transacciones=total_transacciones,
        modificaciones_flujo_caja=modificaciones_flujo_caja,
        exportaciones=exportaciones,
        usuarios_activos=usuarios_activos,
        errores_detectados=errores_detectados,
        ip_addresses_unicas=ip_addresses_unicas
    )

@router.get("/usuario/{usuario_id}/actividad", response_model=AuditoriaUsuario)
def obtener_actividad_usuario(
    usuario_id: int,
    dias: int = Query(30, ge=1, le=365, description="Días hacia atrás para analizar"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador"]))
):
    """
    Obtener estadísticas de actividad para un usuario específico.
    """
    from sqlalchemy import func
    from ..models.auditoria import RegistroAuditoria
    
    fecha_inicio = datetime.now() - timedelta(days=dias)
    
    # Obtener datos del usuario
    query_usuario = db.query(RegistroAuditoria).filter(
        RegistroAuditoria.usuario_id == usuario_id,
        RegistroAuditoria.fecha_hora >= fecha_inicio
    )
    
    # Primera consulta para obtener datos básicos
    primer_registro = query_usuario.first()
    if not primer_registro:
        raise HTTPException(status_code=404, detail="No se encontró actividad para este usuario")
    
    total_acciones = query_usuario.count()
    
    ultima_actividad = query_usuario.order_by(RegistroAuditoria.fecha_hora.desc()).first().fecha_hora
    
    # Acciones por tipo
    acciones_query = db.query(
        RegistroAuditoria.accion,
        func.count(RegistroAuditoria.id).label('total')
    ).filter(
        RegistroAuditoria.usuario_id == usuario_id,
        RegistroAuditoria.fecha_hora >= fecha_inicio
    ).group_by(RegistroAuditoria.accion).all()
    
    acciones_por_tipo = {accion.accion: accion.total for accion in acciones_query}
    
    # Módulos utilizados
    modulos_query = db.query(RegistroAuditoria.modulo).filter(
        RegistroAuditoria.usuario_id == usuario_id,
        RegistroAuditoria.fecha_hora >= fecha_inicio
    ).distinct().all()
    
    modulos_utilizados = [modulo.modulo for modulo in modulos_query]
    
    return AuditoriaUsuario(
        usuario_nombre=primer_registro.usuario_nombre,
        total_acciones=total_acciones,
        ultima_actividad=ultima_actividad,
        acciones_por_tipo=acciones_por_tipo,
        modulos_utilizados=modulos_utilizados
    )

# Endpoint para limpiar registros antiguos (solo administradores)
@router.delete("/limpiar-antiguos")
def limpiar_registros_antiguos(
    dias_antiguedad: int = Query(365, ge=30, description="Eliminar registros más antiguos que X días"),
    confirmar: bool = Query(False, description="Debe ser True para confirmar la eliminación"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_user_role(["Administrador", "administrador"]))
):
    """
    Eliminar registros de auditoría antiguos para mantener el rendimiento.
    CUIDADO: Esta acción no se puede deshacer.
    """
    
    if not confirmar:
        raise HTTPException(
            status_code=400, 
            detail="Debe confirmar la eliminación estableciendo confirmar=true"
        )
    
    from ..models.auditoria import RegistroAuditoria
    
    fecha_limite = datetime.now() - timedelta(days=dias_antiguedad)
    
    registros_a_eliminar = db.query(RegistroAuditoria).filter(
        RegistroAuditoria.fecha_hora < fecha_limite
    ).count()
    
    if registros_a_eliminar == 0:
        return {"mensaje": "No hay registros antiguos para eliminar", "eliminados": 0}
    
    # Eliminar registros
    eliminados = db.query(RegistroAuditoria).filter(
        RegistroAuditoria.fecha_hora < fecha_limite
    ).delete()
    
    db.commit()
    
    # Registrar esta acción
    AuditoriaService.registrar_accion(
        db=db,
        usuario=current_user,
        accion="DELETE",
        modulo="SISTEMA",
        entidad="Registros Auditoría",
        descripcion=f"Eliminó {eliminados} registros de auditoría anteriores a {fecha_limite.date()}"
    )
    
    return {
        "mensaje": f"Se eliminaron {eliminados} registros de auditoría anteriores a {fecha_limite.date()}",
        "eliminados": eliminados
    }