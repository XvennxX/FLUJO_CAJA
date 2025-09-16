"""
API endpoints para gestión de transacciones de flujo de caja
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

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
from ..api.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transacciones-flujo-caja", tags=["Transacciones Flujo de Caja"])

@router.post("/", response_model=TransaccionFlujoCajaResponse, status_code=status.HTTP_201_CREATED)
def crear_transaccion(
    transaccion_data: TransaccionFlujoCajaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear una nueva transacción de flujo de caja"""
    try:
        # 🚫 VALIDACIÓN: Verificar si es un concepto auto-calculado
        conceptos_auto_calculados = [3, 52, 54, 82, 83, 84, 85]  # VENTANILLA, DIFERENCIA SALDOS, SALDO DIA ANTERIOR, SUBTOTAL MOVIMIENTO, etc.
        
        if transaccion_data.concepto_id in conceptos_auto_calculados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede crear manualmente el concepto ID {transaccion_data.concepto_id}. Este valor se calcula automáticamente."
            )
        
        logger.info(f"Creando transacción: concepto_id={transaccion_data.concepto_id}, monto={transaccion_data.monto}, usuario={current_user.id}")
        
        service = TransaccionFlujoCajaService(db)
        transaccion = service.crear_transaccion(transaccion_data, current_user.id)
        
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
    
    # 🔥 AUTO-INICIALIZACIÓN: Asegurar que existe SALDO INICIAL para esta fecha
    dependencias_service = DependenciasFlujoCajaService(db)
    try:
        # Ejecutar auto-cálculo de SALDO INICIAL si es necesario
        dependencias_service._procesar_saldo_inicial_automatico(
            fecha=fecha,
            compania_id=getattr(current_user, "compania_id", 1),
            usuario_id=getattr(current_user, "id", 1)
        )
    except Exception as e:
        # Si hay error, log pero no fallar la consulta
        import logging
        logging.warning(f"Error en auto-inicialización SALDO INICIAL para {fecha}: {e}")
    
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

@router.put("/{transaccion_id}", response_model=TransaccionFlujoCajaResponse)
def actualizar_transaccion(
    transaccion_id: int,
    transaccion_data: TransaccionFlujoCajaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar una transacción existente"""
    logger.info(f"🚨🚨🚨 API PUT /transacciones/{transaccion_id} LLAMADO 🚨🚨🚨")
    logger.info(f"📋 Datos recibidos: {transaccion_data.model_dump()}")
    logger.info(f"👤 Usuario: {current_user.id if hasattr(current_user, 'id') else 'Unknown'}")
    try:
        # � VALIDACIÓN: Verificar si es un concepto auto-calculado
        service = TransaccionFlujoCajaService(db)
        transaccion_existente = service.obtener_transaccion_por_id(transaccion_id)
        
        if not transaccion_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
        
        conceptos_auto_calculados = [3, 52, 54, 82, 83, 84, 85]  # VENTANILLA, DIFERENCIA SALDOS, SALDO DIA ANTERIOR, SUBTOTAL MOVIMIENTO, etc.
        
        if transaccion_existente.concepto_id in conceptos_auto_calculados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede modificar manualmente el concepto ID {transaccion_existente.concepto_id}. Este valor se calcula automáticamente."
            )
        
        print(f"🔄 Actualizando transacción ID {transaccion_id}: {transaccion_data.dict()}")
        print(f"👤 Usuario: {current_user.id}")
        
        transaccion = service.actualizar_transaccion(transaccion_id, transaccion_data, current_user.id)
        
        # 🔥 AUTO-DEPENDENCIAS: Si es pagaduría y concepto crítico, procesar dependencias
        if (transaccion.area == AreaTransaccion.pagaduria):
            # Conceptos que trigger auto-procesamiento: SALDOS EN BANCOS, SALDO DIA ANTERIOR, y conceptos de movimiento (55-81)
            conceptos_trigger = [53, 54] + list(range(55, 82))  # 53, 54, 55, 56, ..., 81
            
            if transaccion.concepto_id in conceptos_trigger:
                dependencias_service = DependenciasFlujoCajaService(db)
                try:
                    dependencias_service.procesar_dependencias_avanzadas(
                        fecha=transaccion.fecha,
                        area=AreaTransaccionSchema.pagaduria,
                        concepto_modificado_id=transaccion.concepto_id,
                        cuenta_id=transaccion.cuenta_id,
                        compania_id=getattr(current_user, "compania_id", 1),
                        usuario_id=current_user.id
                    )
                    print(f"✅ Dependencias de pagaduría procesadas para concepto {transaccion.concepto_id}")
                except Exception as e:
                    print(f"⚠️ Error procesando dependencias pagaduría: {e}")
        
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
    """Actualizar una transacción existente con recálculo automático de dependencias"""
    try:
        # 🚫 VALIDACIÓN: Verificar si es un concepto auto-calculado
        conceptos_auto_calculados = [3, 52, 54, 82, 83, 84, 85]
        
        # Obtener la transacción actual para verificar el concepto
        transaccion_actual = db.query(TransaccionFlujoCaja).filter(TransaccionFlujoCaja.id == transaccion_id).first()
        if not transaccion_actual:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
        
        if transaccion_actual.concepto_id in conceptos_auto_calculados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede modificar manualmente el concepto ID {transaccion_actual.concepto_id}. Este valor se calcula automáticamente."
            )
        
        logger.info(f"�🚨🚨 API PUT /transacciones/{transaccion_id} - MÉTODO 2 LLAMADO 🚨🚨🚨")
        logger.info(f"📋 Datos recibidos método 2: {transaccion_data.model_dump()}")
        logger.info(f"👤 Usuario método 2: {current_user.id}")
        
        service = TransaccionFlujoCajaService(db)
        transaccion = service.actualizar_transaccion(transaccion_id, transaccion_data, current_user.id)
        
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
            
        except Exception as e:
            print(f"⚠️ Error en recálculo completo tras actualización: {e}")
        
        print(f"✅ Transacción actualizada exitosamente: ID {transaccion.id}")
        return transaccion
        
    except ValueError as e:
        print(f"❌ Error de validación en actualización: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"💥 Error interno en actualización: {str(e)}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")

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
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar una transacción"""
    service = TransaccionFlujoCajaService(db)
    eliminado = service.eliminar_transaccion(transaccion_id, current_user.id)
    
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")

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
    
    # 🔥 AUTO-PROCESAMIENTO: Ejecutar dependencias de pagaduría
    dependencias_service = DependenciasFlujoCajaService(db)
    try:
        # Procesar dependencias automáticas de pagaduría
        dependencias_service.procesar_dependencias_avanzadas(
            fecha=fecha,
            area=AreaTransaccionSchema.pagaduria,
            compania_id=getattr(current_user, "compania_id", 1),
            usuario_id=getattr(current_user, "id", 1)
        )
    except Exception as e:
        # Si hay error, log pero no fallar la consulta
        import logging
        logging.warning(f"Error en auto-procesamiento pagaduría para {fecha}: {e}")
    
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
