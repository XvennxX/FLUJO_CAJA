from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime

from app.core.database import get_db
from app.services.report_service import ReportService
from app.services.cash_flow_service import CashFlowService
from app.services.audit_service import AuditService
from app.schemas.reports import (
    ReporteIngresoEgreso, 
    ReporteCuentas, 
    ReporteConceptos,
    ReporteAuditoria,
    DashboardResumen,
    FlujoTiempo,
    FlujoPeriodo,
    SaldosCuentas
)

router = APIRouter()

@router.get("/dashboard", response_model=DashboardResumen)
async def dashboard_resumen(db: Session = Depends(get_db)):
    """Dashboard con métricas principales del sistema"""
    
    # Crear servicios
    audit_service = AuditService(db)
    report_service = ReportService(db, audit_service)
    
    try:
        dashboard_data = report_service.dashboard_resumen()
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar dashboard: {str(e)}"
        )

@router.get("/ingresos-egresos", response_model=ReporteIngresoEgreso)
async def reporte_ingresos_egresos(
    fecha_inicio: date,
    fecha_fin: date,
    id_cuenta: Optional[int] = None,
    id_concepto: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Reporte detallado de ingresos y egresos"""
    
    # Crear servicios
    audit_service = AuditService(db)
    report_service = ReportService(db, audit_service)
    
    try:
        reporte = report_service.reporte_ingresos_egresos(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_cuenta=id_cuenta,
            id_concepto=id_concepto
        )
        
        return reporte
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar reporte: {str(e)}"
        )

@router.get("/cuentas", response_model=ReporteCuentas)
async def reporte_cuentas(db: Session = Depends(get_db)):
    """Reporte de estado de todas las cuentas"""
    
    # Crear servicios
    audit_service = AuditService(db)
    report_service = ReportService(db, audit_service)
    
    try:
        reporte = report_service.reporte_cuentas()
        return reporte
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar reporte de cuentas: {str(e)}"
        )

@router.get("/conceptos", response_model=ReporteConceptos)
async def reporte_conceptos(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db)
):
    """Reporte de uso de conceptos"""
    
    # Crear servicios
    audit_service = AuditService(db)
    report_service = ReportService(db, audit_service)
    
    try:
        reporte = report_service.reporte_conceptos(
            incluir_inactivos=incluir_inactivos
        )
        
        return reporte
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar reporte de conceptos: {str(e)}"
        )

@router.get("/auditoria", response_model=ReporteAuditoria)
async def reporte_auditoria(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    id_usuario: Optional[int] = None,
    accion: Optional[str] = None,
    limite: int = 100,
    db: Session = Depends(get_db)
):
    """Reporte de auditoría del sistema"""
    
    # Crear servicios
    audit_service = AuditService(db)
    report_service = ReportService(db, audit_service)
    
    try:
        reporte = report_service.reporte_auditoria(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_usuario=id_usuario,
            accion=accion,
            limite=limite
        )
        
        return reporte
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar reporte de auditoría: {str(e)}"
        )

@router.get("/flujo-diario", response_model=FlujoTiempo)
async def flujo_diario(
    fecha: date,
    id_cuenta: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Flujo de caja de un día específico"""
    
    # Crear servicios
    cash_flow_service = CashFlowService(db)
    
    try:
        flujo = cash_flow_service.calcular_flujo_diario(
            fecha=fecha,
            id_cuenta=id_cuenta
        )
        
        return flujo
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular flujo diario: {str(e)}"
        )

@router.get("/flujo-periodo", response_model=FlujoPeriodo)
async def flujo_periodo(
    fecha_inicio: date,
    fecha_fin: date,
    id_cuenta: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Flujo de caja por período"""
    
    # Crear servicios
    cash_flow_service = CashFlowService(db)
    
    try:
        flujo = cash_flow_service.calcular_flujo_periodo(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_cuenta=id_cuenta
        )
        
        return flujo
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular flujo del período: {str(e)}"
        )

@router.get("/saldos", response_model=SaldosCuentas)
async def saldos_cuentas(db: Session = Depends(get_db)):
    """Saldos actuales de todas las cuentas"""
    
    # Crear servicios
    cash_flow_service = CashFlowService(db)
    
    try:
        saldos = cash_flow_service.obtener_saldos_cuentas()
        return saldos
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener saldos: {str(e)}"
        )
