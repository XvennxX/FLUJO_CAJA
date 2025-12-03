"""
API endpoints para gestión de transacciones de flujo de caja
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect, Request
from sqlalchemy.orm import Session
from datetime import date
import json

logger = logging.getLogger(__name__)

from ..core.database import get_db
from ..models import TransaccionFlujoCaja, AreaTransaccion
from ..schemas.flujo_caja import (
    TransaccionFlujoCajaCreate,
    TransaccionFlujoCajaUpdate, 
    TransaccionFlujoCajaResponse,
    FlujoCajaDiarioResponse,
    FlujoCajaResumenResponse,
    AreaTransaccionSchema,
    AreaConceptoSchema
)
from ..services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
from ..services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from ..services.concepto_flujo_caja_service import ConceptoFlujoCajaService
from ..core.concepto_utils import es_concepto_auto_calculado
from ..api.auth import get_current_user
from ..core.websocket import websocket_manager
from ..services.auditoria_service import log_transaccion_flujo_caja
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transacciones-flujo-caja", tags=["Transacciones Flujo de Caja"])

@router.post("/", response_model=TransaccionFlujoCajaResponse, status_code=status.HTTP_201_CREATED)
async def crear_transaccion(
    transaccion_data: TransaccionFlujoCajaCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear una nueva transacción de flujo de caja"""
    try:
        # 🚫 VALIDACIÓN: Verificar si es un concepto auto-calculado
        conceptos_auto_calculados = [2, 52, 54, 82, 83, 84, 85]  # CONSUMO, DIFERENCIA SALDOS, SALDO DIA ANTERIOR, SUBTOTAL MOVIMIENTO, etc.
        
        if transaccion_data.concepto_id in conceptos_auto_calculados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede crear manualmente el concepto ID {transaccion_data.concepto_id}. Este valor se calcula automáticamente."
            )
        
        logger.info(f"🔍 API POST: Creando transacción: concepto_id={transaccion_data.concepto_id}, monto={transaccion_data.monto}, area={transaccion_data.area}, tipo_monto={type(transaccion_data.monto)}, usuario={current_user.id}")
        
        service = TransaccionFlujoCajaService(db)
        transaccion = service.crear_transaccion(transaccion_data, current_user.id)
        
        # 📝 AUDITORÍA: Registrar creación de transacción
        try:
            from ..models.conceptos_flujo_caja import ConceptoFlujoCaja
            from ..models.cuentas_bancarias import CuentaBancaria
            
            concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == transaccion_data.concepto_id).first()
            cuenta = db.query(CuentaBancaria).filter(CuentaBancaria.id == transaccion_data.cuenta_id).first()
            
            concepto_nombre = concepto.nombre if concepto else f"Concepto ID {transaccion_data.concepto_id}"
            cuenta_info = f"{cuenta.banco.nombre} - {cuenta.numero_cuenta}" if cuenta else f"Cuenta ID {transaccion_data.cuenta_id}"
            
            log_transaccion_flujo_caja(
                db=db,
                usuario=current_user,
                accion="CREATE",
                fecha=str(transaccion_data.fecha),
                concepto=concepto_nombre,
                cuenta=cuenta_info,
                valor_nuevo=float(transaccion_data.monto),
                request=request
            )
        except Exception as e:
            logger.warning(f"Error en auditoría de creación: {e}")
            # No fallar si hay error en auditoría
        
        # 🔥 AUTO-RECÁLCULO COMPLETO: Procesar AMBOS dashboards para mantener consistencia
        dependencias_service = DependenciasFlujoCajaService(db)
        try:
            resultados_completos = dependencias_service.procesar_dependencias_completas_ambos_dashboards(
                fecha=transaccion_data.fecha,
                concepto_modificado_id=transaccion_data.concepto_id,
                cuenta_id=transaccion_data.cuenta_id,
                compania_id=getattr(current_user, "compania_id", 1),
                usuario_id=current_user.id
            )
            
            total_updates = (
                len(resultados_completos.get("tesoreria", [])) + 
                len(resultados_completos.get("pagaduria", [])) + 
                len(resultados_completos.get("cross_dashboard", []))
            )
            logger.info(f"Recálculo completo ejecutado: {total_updates} actualizaciones en ambos dashboards")
            
        except Exception as e:
            logger.warning(f"Error en recálculo completo: {e}")
            # No falla la creación si hay error en dependencias
        
        # 📡 NOTIFICACIÓN WEBSOCKET: Nueva transacción creada
        try:
            await websocket_manager.broadcast_update({
                "type": "transaccion_created",
                "transaccion_id": transaccion.id,
                "concepto_id": transaccion.concepto_id,
                "area": transaccion.area.value if hasattr(transaccion.area, 'value') else str(transaccion.area),
                "fecha": transaccion.fecha.isoformat(),
                "cuenta_id": transaccion.cuenta_id,
                "monto": float(transaccion.monto),
                "message": f"Nueva transacción creada",
                "user_id": current_user.id
            })
            print(f"📡 Notificación WebSocket enviada: nueva transacción creada")
            
        except Exception as e:
            print(f"⚠️ Error enviando notificación WebSocket: {e}")
        
        print(f"✅ Transacción creada exitosamente: ID {transaccion.id}")
        return transaccion
    except ValueError as e:
        print(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"💥 Error interno: {str(e)}")
        print(f"💥 Tipo de error: {type(e).__name__}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")

@router.get("/fecha/{fecha}", response_model=List[TransaccionFlujoCajaResponse])
def obtener_transacciones_por_fecha(
    fecha: date,
    area: Optional[AreaTransaccionSchema] = Query(None, description="Filtrar por área"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener todas las transacciones de una fecha específica"""
    service = TransaccionFlujoCajaService(db)
    
    # 🔥 AUTO-INICIALIZACIÓN DESHABILITADA TEMPORALMENTE
    # Esta lógica interfiere con las proyecciones de días hábiles
    # dependencias_service = DependenciasFlujoCajaService(db)
    # try:
    #     # Ejecutar auto-cálculo de SALDO INICIAL si es necesario
    #     dependencias_service._procesar_saldo_inicial_automatico(
    #         fecha=fecha,
    #         compania_id=getattr(current_user, "compania_id", 1),
    #         usuario_id=getattr(current_user, "id", 1)
    #     )
    # except Exception as e:
    #     # Si hay error, log pero no fallar la consulta
    #     import logging
    #     logging.warning(f"Error en auto-inicialización SALDO INICIAL para {fecha}: {e}")
    
    transacciones = service.obtener_transacciones_por_fecha(fecha, area)
    return transacciones

@router.get("/{transaccion_id}", response_model=TransaccionFlujoCajaResponse)
def obtener_transaccion(
    transaccion_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener una transacción específica por ID"""
    service = TransaccionFlujoCajaService(db)
    transaccion = service.obtener_transaccion_por_id(transaccion_id)
    
    if not transaccion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
    
    return transaccion

@router.put("/{transaccion_id}/quick", response_model=TransaccionFlujoCajaResponse)
async def actualizar_transaccion_rapida(
    transaccion_id: int,
    transaccion_data: TransaccionFlujoCajaUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """🚀 OPTIMIZADO: Actualizar transacción con respuesta inmediata"""
    logger.info(f"🚀 API PUT RÁPIDO /transacciones/{transaccion_id}/quick LLAMADO")
    logger.info(f"📋 Datos: {transaccion_data.model_dump()}")
    
    try:
        # Validación rápida de concepto auto-calculado
        service = TransaccionFlujoCajaService(db)
        transaccion_existente = service.obtener_transaccion_por_id(transaccion_id)
        
        if not transaccion_existente:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        
        # Verificar si es auto-calculado
        concepto_service = ConceptoFlujoCajaService(db)
        concepto = concepto_service.obtener_concepto_por_id(transaccion_existente.concepto_id)
        
        # Determinar si es auto-calculado usando la función utilitaria
        if concepto and es_concepto_auto_calculado(concepto):
            raise HTTPException(
                status_code=400, 
                detail="No se puede modificar un concepto auto-calculado"
            )
        
        # Guardar valor anterior para auditoría
        valor_anterior = float(transaccion_existente.monto)
        
        # Actualización SOLO de la transacción (sin dependencias inmediatas)
        transaccion = service.actualizar_transaccion_simple(transaccion_id, transaccion_data, current_user.id)
        
        # 📝 AUDITORÍA: Registrar actualización rápida
        try:
            from ..models.conceptos_flujo_caja import ConceptoFlujoCaja
            from ..models.cuentas_bancarias import CuentaBancaria
            
            concepto_obj = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == transaccion.concepto_id).first()
            cuenta = db.query(CuentaBancaria).filter(CuentaBancaria.id == transaccion.cuenta_id).first()
            
            concepto_nombre = concepto_obj.nombre if concepto_obj else f"Concepto ID {transaccion.concepto_id}"
            cuenta_info = f"{cuenta.banco.nombre} - {cuenta.numero_cuenta}" if cuenta else f"Cuenta ID {transaccion.cuenta_id}"
            
            log_transaccion_flujo_caja(
                db=db,
                usuario=current_user,
                accion="UPDATE",
                fecha=str(transaccion.fecha),
                concepto=concepto_nombre,
                cuenta=cuenta_info,
                valor_anterior=valor_anterior,
                valor_nuevo=float(transaccion.monto),
                request=request
            )
            logger.info(f"✅ Auditoría registrada: UPDATE RÁPIDO transacción {transaccion_id}")
        except Exception as e:
            logger.warning(f"Error en auditoría de actualización rápida: {e}")
            # No fallar si hay error en auditoría
        
        # Programar procesamiento de dependencias en background
        from app.services.optimized_transaction_service import optimized_service
        asyncio.create_task(
            optimized_service.procesar_dependencias_async(
                transaccion.fecha,
                transaccion.concepto_id,
                transaccion.cuenta_id,
                current_user.id,
                db
            )
        )
        
        logger.info(f"✅ Transacción {transaccion_id} actualizada INMEDIATAMENTE")
        return transaccion
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en actualización rápida: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{transaccion_id}", response_model=TransaccionFlujoCajaResponse)
async def actualizar_transaccion(
    transaccion_id: int,
    transaccion_data: TransaccionFlujoCajaUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar una transacción existente (método completo tradicional)"""
    logger.info(f"🚨🚨🚨 API PUT /transacciones/{transaccion_id} LLAMADO 🚨🚨🚨")
    logger.info(f"📋 Datos recibidos: {transaccion_data.model_dump()}")
    logger.info(f"👤 Usuario: {current_user.id if hasattr(current_user, 'id') else 'Unknown'}")
    try:
        # � VALIDACIÓN: Verificar si es un concepto auto-calculado
        service = TransaccionFlujoCajaService(db)
        transaccion_existente = service.obtener_transaccion_por_id(transaccion_id)
        
        if not transaccion_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
        
        conceptos_auto_calculados = [2, 52, 54, 82, 83, 84, 85]  # CONSUMO, DIFERENCIA SALDOS, SALDO DIA ANTERIOR, SUBTOTAL MOVIMIENTO, etc.
        
        if transaccion_existente.concepto_id in conceptos_auto_calculados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede modificar manualmente el concepto ID {transaccion_existente.concepto_id}. Este valor se calcula automáticamente."
            )
        
        print(f"🔄 Actualizando transacción ID {transaccion_id}: {transaccion_data.dict()}")
        print(f"👤 Usuario: {current_user.id}")
        
        # Guardar valor anterior para auditoría
        valor_anterior = float(transaccion_existente.monto)
        
        transaccion = service.actualizar_transaccion(transaccion_id, transaccion_data, current_user.id)
        
        # 📝 AUDITORÍA: Registrar actualización de transacción
        try:
            from ..models.conceptos_flujo_caja import ConceptoFlujoCaja
            from ..models.cuentas_bancarias import CuentaBancaria
            
            concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == transaccion.concepto_id).first()
            cuenta = db.query(CuentaBancaria).filter(CuentaBancaria.id == transaccion.cuenta_id).first()
            
            concepto_nombre = concepto.nombre if concepto else f"Concepto ID {transaccion.concepto_id}"
            cuenta_info = f"{cuenta.banco.nombre} - {cuenta.numero_cuenta}" if cuenta else f"Cuenta ID {transaccion.cuenta_id}"
            
            log_transaccion_flujo_caja(
                db=db,
                usuario=current_user,
                accion="UPDATE",
                fecha=str(transaccion.fecha),
                concepto=concepto_nombre,
                cuenta=cuenta_info,
                valor_anterior=valor_anterior,
                valor_nuevo=float(transaccion.monto),
                request=request
            )
            logger.info(f"✅ Auditoría registrada: UPDATE transacción {transaccion_id}")
        except Exception as e:
            logger.warning(f"Error en auditoría de actualización: {e}")
            # No fallar si hay error en auditoría
        
        # 🔥 AUTO-RECÁLCULO COMPLETO: Procesar AMBOS dashboards tras actualización
        dependencias_service = DependenciasFlujoCajaService(db)
        try:
            resultados_completos = dependencias_service.procesar_dependencias_completas_ambos_dashboards(
                fecha=transaccion.fecha,
                concepto_modificado_id=transaccion.concepto_id,
                cuenta_id=transaccion.cuenta_id,
                compania_id=getattr(current_user, "compania_id", 1),
                usuario_id=current_user.id
            )
            
            total_updates = (
                len(resultados_completos.get("tesoreria", [])) + 
                len(resultados_completos.get("pagaduria", [])) + 
                len(resultados_completos.get("cross_dashboard", []))
            )
            print(f"🔄 Recálculo completo tras actualización: {total_updates} actualizaciones en ambos dashboards")
            
            # 📡 NOTIFICACIÓN WEBSOCKET: Enviar actualización en tiempo real
            try:
                await websocket_manager.broadcast_update({
                    "type": "transaccion_updated",
                    "transaccion_id": transaccion.id,
                    "concepto_id": transaccion.concepto_id,
                    "area": transaccion.area.value if hasattr(transaccion.area, 'value') else str(transaccion.area),
                    "fecha": transaccion.fecha.isoformat(),
                    "cuenta_id": transaccion.cuenta_id,
                    "monto_nuevo": float(transaccion.monto),
                    "total_dependencias_actualizadas": total_updates,
                    "message": f"Transacción actualizada - {total_updates} dependencias recalculadas",
                    "user_id": current_user.id
                })
                print(f"📡 Notificación WebSocket enviada: {total_updates} actualizaciones")
                
            except Exception as e:
                print(f"⚠️ Error enviando notificación WebSocket: {e}")
            
        except Exception as e:
            print(f"⚠️ Error en recálculo completo tras actualización: {e}")
        
        print(f"✅ Transacción actualizada exitosamente: ID {transaccion.id}")
        return transaccion
    except ValueError as e:
        print(f"❌ Error de validación en actualización: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"💥 Error interno en actualización: {str(e)}")
        print(f"💥 Tipo de error: {type(e).__name__}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")

# MÉTODO DUPLICADO ELIMINADO - Solo mantenemos el primer método PUT con auto-cálculo

@router.post("/recalcular-dependencias/{fecha}", status_code=status.HTTP_200_OK)
def recalcular_dependencias_fecha(
    fecha: date,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Endpoint para recalcular TODAS las dependencias de una fecha específica.
    Útil para sincronización manual o después de cambios importantes.
    """
    try:
        print(f"🔄 Iniciando recálculo manual para fecha {fecha}")
        
        dependencias_service = DependenciasFlujoCajaService(db)
        resultados_completos = dependencias_service.procesar_dependencias_completas_ambos_dashboards(
            fecha=fecha,
            compania_id=getattr(current_user, "compania_id", 1),
            usuario_id=current_user.id
        )
        
        total_updates = (
            len(resultados_completos.get("tesoreria", [])) + 
            len(resultados_completos.get("pagaduria", [])) + 
            len(resultados_completos.get("cross_dashboard", []))
        )
        
        resultado = {
            "mensaje": f"Recálculo completado para {fecha}",
            "fecha": fecha,
            "total_actualizaciones": total_updates,
            "detalles": {
                "tesoreria_updates": len(resultados_completos.get("tesoreria", [])),
                "pagaduria_updates": len(resultados_completos.get("pagaduria", [])),
                "cross_dashboard_updates": len(resultados_completos.get("cross_dashboard", []))
            },
            "resultados_completos": resultados_completos
        }
        
        print(f"✅ Recálculo manual completado: {total_updates} actualizaciones")
        return resultado
        
    except Exception as e:
        print(f"❌ Error en recálculo manual: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en recálculo: {str(e)}"
        )

@router.delete("/{transaccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transaccion(
    transaccion_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar una transacción"""
    service = TransaccionFlujoCajaService(db)
    
    # Obtener datos de la transacción antes de eliminarla para auditoría
    transaccion_existente = service.obtener_transaccion_por_id(transaccion_id)
    
    if not transaccion_existente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
    
    # Guardar datos para auditoría
    valor_eliminado = float(transaccion_existente.monto)
    fecha_transaccion = str(transaccion_existente.fecha)
    concepto_id = transaccion_existente.concepto_id
    cuenta_id = transaccion_existente.cuenta_id
    
    # Eliminar la transacción
    eliminado = service.eliminar_transaccion(transaccion_id, current_user.id)
    
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
    
    # 📝 AUDITORÍA: Registrar eliminación
    try:
        from ..models.conceptos_flujo_caja import ConceptoFlujoCaja
        from ..models.cuentas_bancarias import CuentaBancaria
        
        concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == concepto_id).first()
        cuenta = db.query(CuentaBancaria).filter(CuentaBancaria.id == cuenta_id).first()
        
        concepto_nombre = concepto.nombre if concepto else f"Concepto ID {concepto_id}"
        cuenta_info = f"{cuenta.banco.nombre} - {cuenta.numero_cuenta}" if cuenta else f"Cuenta ID {cuenta_id}"
        
        log_transaccion_flujo_caja(
            db=db,
            usuario=current_user,
            accion="DELETE",
            fecha=fecha_transaccion,
            concepto=concepto_nombre,
            cuenta=cuenta_info,
            valor_anterior=valor_eliminado,
            request=request
        )
        logger.info(f"✅ Auditoría registrada: DELETE transacción {transaccion_id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de eliminación: {e}")
        # No fallar si hay error en auditoría

# ============================================
# ENDPOINTS PARA REPORTES Y DASHBOARDS
# ============================================

@router.get("/flujo-diario/{fecha}/{area}", response_model=FlujoCajaDiarioResponse)
def obtener_flujo_caja_diario(
    fecha: date,
    area: AreaConceptoSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener el flujo de caja completo de un día específico para un área"""
    service = TransaccionFlujoCajaService(db)
    flujo_diario = service.obtener_flujo_caja_diario(fecha, area)
    return flujo_diario

@router.get("/resumen-periodo/{fecha_inicio}/{fecha_fin}/{area}", response_model=FlujoCajaResumenResponse)
def obtener_resumen_periodo(
    fecha_inicio: date,
    fecha_fin: date,
    area: AreaConceptoSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener resumen del flujo de caja para un período específico"""
    if fecha_inicio > fecha_fin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha de inicio debe ser menor o igual a la fecha de fin")
    
    service = TransaccionFlujoCajaService(db)
    resumen = service.obtener_resumen_periodo(fecha_inicio, fecha_fin, area)
    return resumen

# ============================================
# ENDPOINTS ESPECÍFICOS PARA DASHBOARDS
# ============================================

@router.get("/dashboard/tesoreria/{fecha}", response_model=FlujoCajaDiarioResponse)
def obtener_dashboard_tesoreria(
    fecha: date,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener datos específicos para el dashboard de tesorería"""
    service = TransaccionFlujoCajaService(db)
    flujo_diario = service.obtener_flujo_caja_diario(fecha, AreaConceptoSchema.tesoreria)
    return flujo_diario

@router.get("/dashboard/pagaduria/{fecha}", response_model=FlujoCajaDiarioResponse)
def obtener_dashboard_pagaduria(
    fecha: date,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener datos específicos para el dashboard de pagaduría"""
    
    # 🔥 AUTO-PROCESAMIENTO DESHABILITADO TEMPORALMENTE
    # Interfiere con proyecciones de días hábiles
    # dependencias_service = DependenciasFlujoCajaService(db)
    # try:
    #     # Procesar dependencias automáticas de pagaduría
    #     dependencias_service.procesar_dependencias_avanzadas(
    #         fecha=fecha,
    #         area=AreaTransaccionSchema.pagaduria,
    #         compania_id=getattr(current_user, "compania_id", 1),
    #         usuario_id=getattr(current_user, "id", 1)
    #     )
    # except Exception as e:
    #     # Si hay error, log pero no fallar la consulta
    #     import logging
    #     logging.warning(f"Error en auto-procesamiento pagaduría para {fecha}: {e}")
    
    service = TransaccionFlujoCajaService(db)
    flujo_diario = service.obtener_flujo_caja_diario(fecha, AreaConceptoSchema.pagaduria)
    return flujo_diario

# ============================================
# ENDPOINTS PARA MANEJO MASIVO
# ============================================

@router.post("/importar-masivo")
def importar_transacciones_masivo(
    transacciones: List[TransaccionFlujoCajaCreate],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Importar múltiples transacciones de una vez"""
    service = TransaccionFlujoCajaService(db)
    resultados = {"exitosas": 0, "fallidas": 0, "errores": []}
    
    for i, transaccion_data in enumerate(transacciones):
        try:
            service.crear_transaccion(transaccion_data, current_user.id)
            resultados["exitosas"] += 1
        except Exception as e:
            resultados["fallidas"] += 1
            resultados["errores"].append({
                "indice": i,
                "transaccion": transaccion_data.dict(),
                "error": str(e)
            })
    
    return resultados

@router.delete("/eliminar-fecha/{fecha}")
def eliminar_transacciones_fecha(
    fecha: date,
    area: Optional[AreaTransaccionSchema] = Query(None, description="Área específica a eliminar"),
    confirmar: bool = Query(False, description="Confirmar eliminación"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar todas las transacciones de una fecha específica"""
    if not confirmar:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe confirmar la eliminación con el parámetro 'confirmar=true'")
    
    service = TransaccionFlujoCajaService(db)
    transacciones = service.obtener_transacciones_por_fecha(fecha, area)
    
    eliminadas = 0
    for transaccion in transacciones:
        if service.eliminar_transaccion(transaccion.id, current_user.id):
            eliminadas += 1
    
    return {"message": f"Se eliminaron {eliminadas} transacciones de la fecha {fecha}"}

# ============================================
# WEBSOCKET PARA ACTUALIZACIONES EN TIEMPO REAL
# ============================================

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket para notificaciones en tiempo real de cambios en transacciones
    Conecta clientes para recibir actualizaciones automáticas cuando se modifican datos
    """
    await websocket_manager.connect(websocket)
    
    try:
        # Enviar mensaje de bienvenida
        await websocket_manager.send_personal_message({
            "type": "connection_established",
            "message": "Conexión establecida exitosamente",
            "timestamp": "datetime.now().isoformat()"
        }, websocket)
        
        # Mantener la conexión activa escuchando mensajes del cliente
        while True:
            # Escuchar mensajes del cliente (aunque no los procesemos por ahora)
            data = await websocket.receive_text()
            
            # Opcional: procesar comandos del cliente
            try:
                client_message = json.loads(data)
                if client_message.get("type") == "ping":
                    await websocket_manager.send_personal_message({
                        "type": "pong",
                        "message": "Conexión activa"
                    }, websocket)
            except json.JSONDecodeError:
                logger.warning(f"Mensaje JSON inválido recibido: {data}")
                
    except WebSocketDisconnect:
        logger.info("🔌 Cliente desconectado del WebSocket")
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ Error en WebSocket: {e}")
        websocket_manager.disconnect(websocket)

@router.get("/ws/stats")
async def get_websocket_stats():
    """Obtener estadísticas de conexiones WebSocket activas"""
    return {
        "status": "WebSocket endpoint active",
        "stats": websocket_manager.get_connection_stats(),
        "endpoint": "/api/v1/api/transacciones-flujo-caja/ws"
    }
