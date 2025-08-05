from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ReporteIngresoEgreso(BaseModel):
    """Schema para reporte de ingresos y egresos"""
    periodo: Dict[str, date]
    filtros: Dict[str, Optional[int]]
    resumen: Dict[str, Any]
    ingresos_por_concepto: List[Dict[str, Any]]
    egresos_por_concepto: List[Dict[str, Any]]
    detalle_ingresos: List[Dict[str, Any]]
    detalle_egresos: List[Dict[str, Any]]

class ReporteCuentas(BaseModel):
    """Schema para reporte de cuentas"""
    fecha_reporte: datetime
    resumen: Dict[str, Any]
    detalle_cuentas: List[Dict[str, Any]]

class ReporteConceptos(BaseModel):
    """Schema para reporte de conceptos"""
    fecha_reporte: datetime
    incluir_inactivos: bool
    resumen: Dict[str, Any]
    detalle_conceptos: List[Dict[str, Any]]

class ReporteAuditoria(BaseModel):
    """Schema para reporte de auditoría"""
    fecha_reporte: datetime
    filtros: Dict[str, Any]
    resumen: Dict[str, Any]
    estadisticas_acciones: List[Dict[str, Any]]
    estadisticas_usuarios: List[Dict[str, Any]]
    detalle_registros: List[Dict[str, Any]]

class DashboardResumen(BaseModel):
    """Schema para datos del dashboard"""
    fecha_consulta: datetime
    metricas_diarias: Dict[str, float]
    metricas_semanales: Dict[str, float]
    metricas_mensuales: Dict[str, float]
    saldo_total: float
    transacciones_recientes: List[Dict[str, Any]]

class FlujoTiempo(BaseModel):
    """Schema para flujo de caja en el tiempo"""
    fecha: date
    id_cuenta: Optional[int] = None
    resumen: Dict[str, float]
    ingresos_por_concepto: List[Dict[str, Any]]
    egresos_por_concepto: List[Dict[str, Any]]

class FlujoPeriodo(BaseModel):
    """Schema para flujo de caja por período"""
    periodo: Dict[str, date]
    id_cuenta: Optional[int] = None
    resumen: Dict[str, Any]
    flujo_diario: List[Dict[str, Any]]

class SaldosCuentas(BaseModel):
    """Schema para saldos de cuentas"""
    cuentas: List[Dict[str, Any]]
    total_general: float
    fecha_consulta: datetime

class ProyeccionFlujo(BaseModel):
    """Schema para proyección de flujo"""
    base_calculo: Dict[str, Any]
    proyecciones: List[Dict[str, Any]]

class AnalisisTendencias(BaseModel):
    """Schema para análisis de tendencias"""
    periodo_analisis: str
    tendencias_semanales: List[Dict[str, Any]]
    analisis: Optional[Dict[str, Any]] = None
    mensaje: Optional[str] = None
