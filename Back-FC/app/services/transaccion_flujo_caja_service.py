"""
Servicios para el manejo de transacciones de flujo de caja
Lógica de negocio para CRUD, cálculos automáticos y reportes
"""
import logging
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from datetime import date, datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

from ..models import (
    ConceptoFlujoCaja, TransaccionFlujoCaja, CuentaBancaria, Usuario,
    AreaConcepto, AreaTransaccion, TipoMovimiento, TipoDependencia
)
from ..models.gmf_config import GMFConfig
from ..schemas.flujo_caja import (
    TransaccionFlujoCajaCreate, 
    TransaccionFlujoCajaUpdate, 
    FlujoCajaDiarioResponse,
    FlujoCajaDiarioItem,
    FlujoCajaResumenResponse,
    AreaConceptoSchema,
    AreaTransaccionSchema,
    TipoMovimientoSchema
)
from .dependencias_flujo_caja_service import DependenciasFlujoCajaService

class TransaccionFlujoCajaService:
    """Servicio para gestión de transacciones de flujo de caja"""
    
    def __init__(self, db: Session):
        self.db = db
        self.dependencias_service = DependenciasFlujoCajaService(db)
    
    def _aplicar_signo_por_tipo_concepto(self, monto: float, concepto_id: int) -> float:
        """
        Aplica el signo correcto al monto según el CODIGO del concepto:
        - I (INGRESO): Siempre positivo 
        - E (EGRESO): Siempre negativo
        - N (NEUTRAL): Mantiene el signo que ingrese el usuario
        """
        try:
            logger.info(f"🔍 _aplicar_signo_por_tipo_concepto ENTRADA: monto={monto}, concepto_id={concepto_id}, tipo_monto={type(monto)}")
            
            # Obtener el concepto y su código
            concepto = self.db.query(ConceptoFlujoCaja).filter(
                ConceptoFlujoCaja.id == concepto_id
            ).first()
            
            if not concepto:
                logger.warning(f"⚠️ Concepto ID {concepto_id} no encontrado, manteniendo monto original: {monto}")
                return monto
            
            codigo = concepto.codigo or ""
            monto_absoluto = abs(monto)
            
            logger.info(f"🔍 Concepto encontrado: nombre={concepto.nombre}, codigo='{codigo}'")
            
            if codigo == "I":
                # INGRESO: Siempre positivo
                resultado = monto_absoluto
                logger.info(f"💰 INGRESO: monto_original={monto} → resultado={resultado} (concepto: {concepto.nombre})")
                return resultado
                
            elif codigo == "E":
                # EGRESO: Siempre negativo  
                resultado = -monto_absoluto
                logger.info(f"💸 EGRESO: monto_original={monto} → resultado={resultado} (concepto: {concepto.nombre})")
                return resultado
                
            else:  # codigo == "N" o cualquier otro
                # NEUTRAL: Mantiene el signo del usuario
                logger.info(f"⚖️ NEUTRAL: monto_original={monto} → resultado={monto} (concepto: {concepto.nombre}, código: '{codigo}')")
                logger.info(f"🔍 NEUTRAL DETALLE: monto < 0 = {monto < 0}, monto > 0 = {monto > 0}, monto == 0 = {monto == 0}")
                return monto
                
        except Exception as e:
            logger.error(f"❌ Error aplicando signo por tipo concepto: {e}")
            return monto  # En caso de error, mantener el monto original
    
    def crear_transaccion(self, transaccion_data: TransaccionFlujoCajaCreate, usuario_id: int) -> TransaccionFlujoCaja:
        """Crear una nueva transacción de flujo de caja"""
        
        # 🔍 DEBUG: Log del monto recibido ANTES de cualquier procesamiento
        logger.info(f"🔍 DEBUG crear_transaccion: monto ORIGINAL recibido = {transaccion_data.monto}, concepto_id = {transaccion_data.concepto_id}")
        
        # Validar que el concepto existe y está activo
        concepto = self.db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.id == transaccion_data.concepto_id,
            ConceptoFlujoCaja.activo == 1
        ).first()
        
        if not concepto:
            raise ValueError(f"El concepto ID {transaccion_data.concepto_id} no existe o no está activo")
        
        # Validar que la cuenta existe si se especifica
        if transaccion_data.cuenta_id:
            cuenta = self.db.query(CuentaBancaria).filter(CuentaBancaria.id == transaccion_data.cuenta_id).first()
            if not cuenta:
                raise ValueError(f"La cuenta ID {transaccion_data.cuenta_id} no existe")
        
        # Verificar duplicados (fecha + concepto + cuenta debe ser único)
        transaccion_existente = self.db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == transaccion_data.fecha,
            TransaccionFlujoCaja.concepto_id == transaccion_data.concepto_id,
            TransaccionFlujoCaja.cuenta_id == transaccion_data.cuenta_id
        ).first()
        
        if transaccion_existente:
            raise ValueError("Ya existe una transacción para esta fecha, concepto y cuenta")
        
        # 🔥 APLICAR SIGNO CORRECTO según el tipo de concepto
        monto_original = transaccion_data.monto
        monto_corregido = self._aplicar_signo_por_tipo_concepto(monto_original, transaccion_data.concepto_id)
        
        # Crear data corregida
        transaccion_data_corregida = transaccion_data.dict()
        transaccion_data_corregida['monto'] = monto_corregido
        
        # Crear la transacción
        db_transaccion = TransaccionFlujoCaja(
            **transaccion_data_corregida,
            usuario_id=usuario_id,
            auditoria={
                "accion": "creacion",
                "usuario_id": usuario_id,
                "timestamp": datetime.now().isoformat(),
                "ip": None  # Se puede agregar desde el endpoint
            }
        )
        
        self.db.add(db_transaccion)
        self.db.commit()
        self.db.refresh(db_transaccion)
        
        # � RECÁLCULOS DIRECTOS CLAVE - PRIMERO (GMF y 4x1000 antes de subtotales)
        try:
            # Si se crea uno de los componentes base (1,2,3), recalcular SALDO NETO INICIAL PAGADURÍA (ID 4)
            if transaccion_data.concepto_id in (1, 2, 3) and transaccion_data.cuenta_id:
                self.dependencias_service.recalcular_saldo_neto_inicial_pagaduria(
                    fecha=transaccion_data.fecha,
                    cuenta_id=transaccion_data.cuenta_id,
                    usuario_id=usuario_id,
                    compania_id=transaccion_data.compania_id
                )

            # Recalcular GMF para la cuenta/fecha según configuración vigente
            if transaccion_data.cuenta_id:
                self.dependencias_service.recalcular_gmf(
                    fecha=transaccion_data.fecha,
                    cuenta_id=transaccion_data.cuenta_id,
                    usuario_id=usuario_id,
                    compania_id=transaccion_data.compania_id
                )
            
            # Recalcular CUATRO POR MIL para la cuenta/fecha según configuración vigente (Pagaduría)
            if transaccion_data.cuenta_id:
                self.dependencias_service.recalcular_cuatro_por_mil(
                    fecha=transaccion_data.fecha,
                    cuenta_id=transaccion_data.cuenta_id,
                    usuario_id=usuario_id,
                    compania_id=transaccion_data.compania_id
                )
            # Asegurar escritura de GMF y 4x1000 antes de calcular subtotales
            self.db.commit()
        except Exception as e:
            logger.warning(f"⚠️ Error en recálculos directos GMF/4x1000: {e}")

        # 🔥 AUTO-RECÁLCULO COMPLETO: Procesar AMBOS dashboards DESPUÉS de GMF y 4x1000
        # para que los subtotales incluyan los valores actualizados
        self.dependencias_service.procesar_dependencias_completas_ambos_dashboards(
            fecha=transaccion_data.fecha,
            concepto_modificado_id=transaccion_data.concepto_id,
            cuenta_id=transaccion_data.cuenta_id,
            compania_id=transaccion_data.compania_id,
            usuario_id=usuario_id
        )
        
        return db_transaccion
    
    def obtener_transacciones_por_fecha(self, fecha: date, area: Optional[AreaTransaccionSchema] = None) -> List[TransaccionFlujoCaja]:
        """Obtener todas las transacciones de una fecha específica"""
        query = self.db.query(TransaccionFlujoCaja).filter(TransaccionFlujoCaja.fecha == fecha)
        
        if area:
            query = query.filter(TransaccionFlujoCaja.area == area)
        
        return query.options(joinedload(TransaccionFlujoCaja.concepto)).all()
    
    def obtener_transaccion_por_id(self, transaccion_id: int) -> Optional[TransaccionFlujoCaja]:
        """Obtener transacción por ID"""
        return self.db.query(TransaccionFlujoCaja).options(
            joinedload(TransaccionFlujoCaja.concepto),
            joinedload(TransaccionFlujoCaja.cuenta)
        ).filter(TransaccionFlujoCaja.id == transaccion_id).first()
    
    def actualizar_transaccion(self, transaccion_id: int, transaccion_data: TransaccionFlujoCajaUpdate, usuario_id: int) -> Optional[TransaccionFlujoCaja]:
        """Actualizar una transacción existente"""
        db_transaccion = self.obtener_transaccion_por_id(transaccion_id)
        if not db_transaccion:
            return None
        
        # Actualizar campos
        update_data = transaccion_data.model_dump(exclude_unset=True)
        
        # 🔍 DEBUG: Log del monto recibido ANTES de cualquier procesamiento
        if 'monto' in update_data:
            logger.info(f"🔍 DEBUG actualizar_transaccion: monto ORIGINAL recibido = {update_data['monto']}, concepto_id = {db_transaccion.concepto_id}")
        
        # Guardar valores originales para auditoría
        valores_originales = {
            "fecha": db_transaccion.fecha,
            "concepto_id": db_transaccion.concepto_id,
            "cuenta_id": db_transaccion.cuenta_id,
            "monto": str(db_transaccion.monto),
            "descripcion": db_transaccion.descripcion
        }
        
        # 🔥 APLICAR SIGNO CORRECTO si se está actualizando el monto
        if 'monto' in update_data:
            monto_original = update_data['monto']
            monto_corregido = self._aplicar_signo_por_tipo_concepto(monto_original, db_transaccion.concepto_id)
            update_data['monto'] = monto_corregido
        
        for field, value in update_data.items():
            setattr(db_transaccion, field, value)
        
        # Actualizar auditoría
        auditoria_actual = db_transaccion.auditoria or {}
        auditoria_actual.update({
            "ultima_modificacion": {
                "accion": "actualizacion",
                "usuario_id": usuario_id,
                "timestamp": datetime.now().isoformat(),
                "valores_anteriores": valores_originales,
                "ip": None
            }
        })
        db_transaccion.auditoria = auditoria_actual
        
        self.db.commit()
        self.db.refresh(db_transaccion)
        
        # 🔥 AUTO-RECÁLCULO COMPLETO: Procesar AMBOS dashboards cuando se actualiza una transacción
        logger.info(f"🔍 DEBUG actualizar_transaccion: update_data = {update_data}")
        logger.info(f"🔍 DEBUG: 'fecha' in update_data = {'fecha' in update_data}")
        logger.info(f"🔍 DEBUG: 'area' in update_data = {'area' in update_data}")
        logger.info(f"🔍 DEBUG: 'monto' in update_data = {'monto' in update_data}")
        
        if 'fecha' in update_data or 'area' in update_data or 'monto' in update_data:
            logger.info(f"🎯 DEBUG: CONDICIÓN CUMPLIDA - Ejecutando auto-cálculo...")
            fecha_procesar = update_data.get('fecha', db_transaccion.fecha)

            # Flush previo
            self.db.flush()
            logger.info("🔄 DEBUG: flush() ejecutado antes del recálculo completo")

            # PRIMERO: Recalculo directo saldo neto inicial pagaduría si concepto base afectado
            if db_transaccion.concepto_id in (1,2,3):
                try:
                    resultado_saldo_neto = self.dependencias_service.recalcular_saldo_neto_inicial_pagaduria(
                        fecha=fecha_procesar,
                        cuenta_id=db_transaccion.cuenta_id,
                        usuario_id=usuario_id,
                        compania_id=db_transaccion.compania_id
                    )
                    logger.info(f"🔁 DEBUG: Recalculo directo saldo neto inicial resultado: {resultado_saldo_neto}")
                except Exception as e:
                    logger.warning(f"⚠️ Error recálculo directo saldo neto inicial: {e}")

            # SEGUNDO: Recalculo GMF para la cuenta con la configuración vigente a la fecha (si existe)
            if db_transaccion.cuenta_id:
                try:
                    resultado_gmf = self.dependencias_service.recalcular_gmf(
                        fecha=fecha_procesar,
                        cuenta_id=db_transaccion.cuenta_id,
                        usuario_id=usuario_id,
                        compania_id=db_transaccion.compania_id
                    )
                    logger.info(f"🔁 DEBUG: Recalculo GMF directo resultado: {resultado_gmf}")
                except Exception as e:
                    logger.warning(f"⚠️ Error recálculo GMF directo: {e}")
            
            # TERCERO: Recalculo CUATRO POR MIL para la cuenta con la configuración vigente (Pagaduría)
            if db_transaccion.cuenta_id:
                try:
                    resultado_cpm = self.dependencias_service.recalcular_cuatro_por_mil(
                        fecha=fecha_procesar,
                        cuenta_id=db_transaccion.cuenta_id,
                        usuario_id=usuario_id,
                        compania_id=db_transaccion.compania_id
                    )
                    logger.info(f"🔁 DEBUG: Recalculo 4x1000 directo resultado: {resultado_cpm}")
                except Exception as e:
                    logger.warning(f"⚠️ Error recálculo 4x1000 directo: {e}")
            
            # CUARTO: Recalculo completo de subtotales DESPUÉS de GMF y 4x1000
            resultado_dependencias = self.dependencias_service.procesar_dependencias_completas_ambos_dashboards(
                fecha=fecha_procesar,
                concepto_modificado_id=db_transaccion.concepto_id,
                cuenta_id=db_transaccion.cuenta_id,
                compania_id=db_transaccion.compania_id,
                usuario_id=usuario_id
            )
            logger.info(f"✅ DEBUG: Auto-cálculo completo ejecutado")
        else:
            logger.info(f"❌ DEBUG: CONDICIÓN NO CUMPLIDA - Auto-cálculo NO ejecutado")
        
        return db_transaccion
    
    def eliminar_transaccion(self, transaccion_id: int, usuario_id: int) -> bool:
        """Eliminar una transacción"""
        db_transaccion = self.obtener_transaccion_por_id(transaccion_id)
        if not db_transaccion:
            return False
        
        fecha = db_transaccion.fecha
        area = db_transaccion.area
        concepto_id = db_transaccion.concepto_id
        
        self.db.delete(db_transaccion)
        self.db.commit()
        
        # 🔥 AUTO-RECÁLCULO COMPLETO: Procesar AMBOS dashboards después de eliminar
        self.dependencias_service.procesar_dependencias_completas_ambos_dashboards(
            fecha=fecha,
            concepto_modificado_id=concepto_id,
            usuario_id=usuario_id
        )
        
        return True
    
    def obtener_flujo_caja_diario(self, fecha: date, area: AreaConceptoSchema) -> FlujoCajaDiarioResponse:
        """Obtener el flujo de caja completo de un día específico"""
        
        # Obtener conceptos del área ordenados
        conceptos_query = self.db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.activo == 1
        )
        
        if area != AreaConceptoSchema.ambas:
            conceptos_query = conceptos_query.filter(or_(
                ConceptoFlujoCaja.area == area,
                ConceptoFlujoCaja.area == AreaConcepto.ambas
            ))
        
        conceptos = conceptos_query.order_by(ConceptoFlujoCaja.orden_display).all()
        
        # Obtener transacciones del día
        area_transaccion = AreaTransaccion.tesoreria if area == AreaConceptoSchema.tesoreria else AreaTransaccion.pagaduria
        transacciones = self.db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha,
            TransaccionFlujoCaja.area == area_transaccion
        ).all()
        
        # Crear diccionario de montos por concepto
        montos_por_concepto = {}
        for transaccion in transacciones:
            concepto_id = transaccion.concepto_id
            if concepto_id not in montos_por_concepto:
                montos_por_concepto[concepto_id] = Decimal('0.00')
            montos_por_concepto[concepto_id] += transaccion.monto
        
        # Crear items del flujo de caja
        items = []
        totales = {"ingreso": Decimal('0.00'), "egreso": Decimal('0.00'), "neutral": Decimal('0.00')}
        
        for concepto in conceptos:
            monto = montos_por_concepto.get(concepto.id, Decimal('0.00'))
            
            item = FlujoCajaDiarioItem(
                concepto_id=concepto.id,
                concepto_nombre=concepto.nombre,
                concepto_codigo=concepto.codigo,
                concepto_tipo=TipoMovimientoSchema(concepto.tipo.value),
                orden_display=concepto.orden_display,
                monto=monto
            )
            items.append(item)
            
            # Acumular totales
            totales[concepto.tipo.value] += monto
        
        # Calcular saldo neto
        totales["saldo_neto"] = totales["ingreso"] - totales["egreso"]
        
        return FlujoCajaDiarioResponse(
            fecha=fecha,
            area=area,
            conceptos=items,
            totales=totales
        )
    
    def obtener_resumen_periodo(self, fecha_inicio: date, fecha_fin: date, area: AreaConceptoSchema) -> FlujoCajaResumenResponse:
        """Obtener resumen del flujo de caja para un período"""
        
        # Mapear área de concepto a área de transacción
        area_transaccion = AreaTransaccion.tesoreria if area == AreaConceptoSchema.tesoreria else AreaTransaccion.pagaduria
        
        # Query base para transacciones del período
        transacciones_query = self.db.query(TransaccionFlujoCaja).join(ConceptoFlujoCaja).filter(
            TransaccionFlujoCaja.fecha >= fecha_inicio,
            TransaccionFlujoCaja.fecha <= fecha_fin,
            TransaccionFlujoCaja.area == area_transaccion
        )
        
        # Calcular totales por tipo
        total_ingresos = transacciones_query.filter(ConceptoFlujoCaja.tipo == TipoMovimiento.ingreso).with_entities(
            func.coalesce(func.sum(TransaccionFlujoCaja.monto), 0)
        ).scalar() or Decimal('0.00')
        
        total_egresos = transacciones_query.filter(ConceptoFlujoCaja.tipo == TipoMovimiento.egreso).with_entities(
            func.coalesce(func.sum(TransaccionFlujoCaja.monto), 0)
        ).scalar() or Decimal('0.00')
        
        # Contar transacciones
        transacciones_count = transacciones_query.count()
        
        # Calcular saldo neto
        saldo_neto = total_ingresos - total_egresos
        
        return FlujoCajaResumenResponse(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            area=area,
            total_ingresos=total_ingresos,
            total_egresos=total_egresos,
            saldo_neto=saldo_neto,
            transacciones_count=transacciones_count
        )
    
    def _procesar_dependencias_automaticas(self, fecha: date, area: AreaTransaccionSchema, usuario_id: int):
        """Procesar dependencias automáticas para una fecha específica"""
        
        # Obtener conceptos con dependencias
        area_concepto = AreaConcepto.tesoreria if area == AreaTransaccionSchema.tesoreria else AreaConcepto.pagaduria
        
        conceptos_dependientes = self.db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.depende_de_concepto_id.isnot(None),
            ConceptoFlujoCaja.activo == 1,
            or_(ConceptoFlujoCaja.area == area_concepto, ConceptoFlujoCaja.area == AreaConcepto.ambas)
        ).all()
        
        for concepto in conceptos_dependientes:
            # Obtener valor del concepto del cual depende
            concepto_origen = self.db.query(ConceptoFlujoCaja).filter(
                ConceptoFlujoCaja.id == concepto.depende_de_concepto_id
            ).first()
            
            if not concepto_origen:
                continue
            
            # Obtener transacción origen
            transaccion_origen = self.db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha,
                TransaccionFlujoCaja.concepto_id == concepto_origen.id,
                TransaccionFlujoCaja.area == area
            ).first()
            
            if not transaccion_origen:
                continue
            
            # Calcular nuevo valor según tipo de dependencia
            nuevo_monto = Decimal('0.00')
            if concepto.tipo_dependencia == TipoDependencia.copia:
                nuevo_monto = transaccion_origen.monto
            elif concepto.tipo_dependencia == TipoDependencia.suma:
                # Aquí se podría implementar suma de múltiples conceptos
                nuevo_monto = transaccion_origen.monto
            elif concepto.tipo_dependencia == TipoDependencia.resta:
                # Aquí se podría implementar resta de múltiples conceptos
                nuevo_monto = -transaccion_origen.monto
            
            # Crear o actualizar transacción dependiente
            transaccion_dependiente = self.db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha,
                TransaccionFlujoCaja.concepto_id == concepto.id,
                TransaccionFlujoCaja.area == area
            ).first()
            
            if transaccion_dependiente:
                # Actualizar existente
                transaccion_dependiente.monto = nuevo_monto
                transaccion_dependiente.auditoria = {
                    "accion": "actualizacion_automatica",
                    "dependencia_de": concepto_origen.id,
                    "tipo_dependencia": concepto.tipo_dependencia.value,
                    "timestamp": datetime.now().isoformat(),
                    "sistema": True
                }
            else:
                # Crear nueva
                transaccion_dependiente = TransaccionFlujoCaja(
                    fecha=fecha,
                    concepto_id=concepto.id,
                    cuenta_id=transaccion_origen.cuenta_id,  # Usar la misma cuenta
                    monto=nuevo_monto,
                    descripcion=f"Generado automáticamente desde {concepto_origen.nombre}",
                    usuario_id=usuario_id,
                    area=area,
                    auditoria={
                        "accion": "creacion_automatica",
                        "dependencia_de": concepto_origen.id,
                        "tipo_dependencia": concepto.tipo_dependencia.value,
                        "timestamp": datetime.now().isoformat(),
                        "sistema": True
                    }
                )
                self.db.add(transaccion_dependiente)
        
        self.db.commit()
    
    def actualizar_transaccion(
        self, 
        transaccion_id: int, 
        transaccion_data: TransaccionFlujoCajaUpdate, 
        usuario_id: int
    ) -> TransaccionFlujoCaja:
        """Actualizar una transacción existente"""
        # Buscar la transacción
        transaccion = self.db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.id == transaccion_id
        ).first()
        
        if not transaccion:
            raise ValueError("Transacción no encontrada")
        
        # Guardar valores anteriores para auditoría
        valores_anteriores = {
            "monto": float(transaccion.monto),
            "descripcion": transaccion.descripcion,
            "fecha": transaccion.fecha.isoformat()
        }
        
        # Actualizar campos
        for field, value in transaccion_data.dict(exclude_unset=True).items():
            setattr(transaccion, field, value)
        
        # Actualizar auditoría
        auditoria_actual = transaccion.auditoria or {}
        auditoria_actual.update({
            "accion": "actualizacion",
            "usuario_id": usuario_id,
            "timestamp": datetime.now().isoformat(),
            "valores_anteriores": valores_anteriores,
            "campos_modificados": list(transaccion_data.dict(exclude_unset=True).keys())
        })
        transaccion.auditoria = auditoria_actual
        
        self.db.commit()
        self.db.refresh(transaccion)
        
        return transaccion
    
    def actualizar_transaccion_simple(
        self, 
        transaccion_id: int, 
        transaccion_data: TransaccionFlujoCajaUpdate, 
        usuario_id: int
    ) -> TransaccionFlujoCaja:
        """🚀 OPTIMIZADO: Actualiza transacción SIN procesar dependencias inmediatamente"""
        
        # Buscar la transacción
        transaccion = self.db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.id == transaccion_id
        ).first()
        
        if not transaccion:
            raise ValueError("Transacción no encontrada")
        
        # Guardar valores anteriores para auditoría
        valores_anteriores = {
            "monto": float(transaccion.monto),
            "descripcion": transaccion.descripcion,
        }
        
        # Actualizar campos con lógica de signos
        update_data = transaccion_data.dict(exclude_unset=True)
        
        # 🔍 DEBUG: Log del monto recibido ANTES de cualquier procesamiento
        if 'monto' in update_data:
            logger.info(f"🔍 DEBUG actualizar_transaccion_simple: monto ORIGINAL recibido = {update_data['monto']}, concepto_id = {transaccion.concepto_id}")
        
        # 🔥 APLICAR SIGNO CORRECTO si se está actualizando el monto
        if 'monto' in update_data:
            monto_original = update_data['monto']
            monto_corregido = self._aplicar_signo_por_tipo_concepto(monto_original, transaccion.concepto_id)
            update_data['monto'] = monto_corregido
            logger.info(f"🔍 DEBUG actualizar_transaccion_simple: monto CORREGIDO = {monto_corregido}")
        
        for field, value in update_data.items():
            setattr(transaccion, field, value)
        
        # Auditoría mínima
        auditoria_actual = transaccion.auditoria or {}
        auditoria_actual.update({
            "accion": "actualizacion_rapida",
            "usuario_id": usuario_id,
            "timestamp": datetime.now().isoformat(),
            "valores_anteriores": valores_anteriores,
            "nota": "Actualización optimizada - dependencias en proceso"
        })
        transaccion.auditoria = auditoria_actual
        
        # Commit inmediato
        self.db.commit()
        self.db.refresh(transaccion)
        
        # 🔄 RECÁLCULO GMF: Si se actualizó el monto y hay cuenta asociada, recalcular GMF
        if 'monto' in update_data and transaccion.cuenta_id:
            try:
                logger.info(f"🔁 Recalculando GMF después de actualización simple para cuenta {transaccion.cuenta_id}")
                self.dependencias_service.recalcular_gmf(
                    fecha=transaccion.fecha,
                    cuenta_id=transaccion.cuenta_id,
                    usuario_id=usuario_id,
                    compania_id=transaccion.compania_id
                )
                self.db.commit()
            except Exception as e:
                logger.warning(f"⚠️ Error recalculando GMF en actualización simple: {e}")
        
        # 🔄 RECÁLCULO 4x1000: Si se actualizó el monto y hay cuenta asociada, recalcular Cuatro por Mil
        if 'monto' in update_data and transaccion.cuenta_id:
            try:
                logger.info(f"🔁 Recalculando 4x1000 después de actualización simple para cuenta {transaccion.cuenta_id}")
                self.dependencias_service.recalcular_cuatro_por_mil(
                    fecha=transaccion.fecha,
                    cuenta_id=transaccion.cuenta_id,
                    usuario_id=usuario_id,
                    compania_id=transaccion.compania_id
                )
                self.db.commit()
            except Exception as e:
                logger.warning(f"⚠️ Error recalculando 4x1000 en actualización simple: {e}")
        
        # 🔄 RECÁLCULO SUBTOTALES: Después de GMF y 4x1000, recalcular dependencias completas
        if 'monto' in update_data and transaccion.cuenta_id:
            try:
                logger.info(f"🔁 Recalculando subtotales después de actualización simple")
                self.dependencias_service.procesar_dependencias_completas_ambos_dashboards(
                    fecha=transaccion.fecha,
                    concepto_modificado_id=transaccion.concepto_id,
                    cuenta_id=transaccion.cuenta_id,
                    compania_id=transaccion.compania_id,
                    usuario_id=usuario_id
                )
                self.db.commit()
            except Exception as e:
                logger.warning(f"⚠️ Error recalculando subtotales en actualización simple: {e}")
        
        return transaccion
    
    def eliminar_transaccion(self, transaccion_id: int, usuario_id: int) -> bool:
        """Eliminar una transacción"""
        transaccion = self.db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.id == transaccion_id
        ).first()
        
        if not transaccion:
            return False
        
        # Auditoría de eliminación
        logger.info(f"Eliminando transacción ID {transaccion_id} por usuario {usuario_id}")
        
        self.db.delete(transaccion)
        self.db.commit()
        
        return True
