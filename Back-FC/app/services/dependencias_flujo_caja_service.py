"""
Servicio avanzado para el manejo de dependencias entre conceptos de flujo de caja.
Soporta múltiples conceptos, cálculos complejos y notificaciones en tiempo real.
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from app.models.conceptos_flujo_caja import ConceptoFlujoCaja, TipoDependencia, AreaConcepto
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.cuentas_bancarias import CuentaBancaria
from app.schemas.flujo_caja import AreaTransaccionSchema
from app.services.dias_habiles_service import DiasHabilesService

logger = logging.getLogger(__name__)

class DependenciasFlujoCajaService:
    """
    Servicio especializado para manejar dependencias complejas entre conceptos.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.dias_habiles_service = DiasHabilesService(db)
    
    def _convertir_area_a_enum(self, area: AreaTransaccionSchema) -> AreaTransaccion:
        """Convierte área de transacción schema a enum de base de datos"""
        if area == AreaTransaccionSchema.tesoreria or area == 'TESORERIA':
            return AreaTransaccion.tesoreria
        elif area == AreaTransaccionSchema.pagaduria or area == 'PAGADURIA':
            return AreaTransaccion.pagaduria
        else:
            return AreaTransaccion.tesoreria  # Default
    
    def procesar_dependencias_completas_ambos_dashboards(
        self,
        fecha: date,
        concepto_modificado_id: Optional[int] = None,
        cuenta_id: Optional[int] = None,
        compania_id: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> Dict[str, List[Dict]]:
        """
        Procesa TODAS las dependencias en AMBOS dashboards (tesorería y pagaduría)
        cuando cualquier valor cambia. Esto asegura consistencia total.
        """
        try:
            logger.info(f"🔄 Iniciando recálculo completo para ambos dashboards - Fecha: {fecha}")
            
            resultados = {
                "tesoreria": [],
                "pagaduria": [],
                "cross_dashboard": []
            }
            
            # 1. PROCESAR TESORERÍA PRIMERO (porque pagaduría depende de tesorería)
            logger.info("📊 Procesando dependencias de TESORERÍA...")
            try:
                resultados_tesoreria = self.procesar_dependencias_avanzadas(
                    fecha=fecha,
                    area=AreaTransaccionSchema.tesoreria,
                    concepto_modificado_id=concepto_modificado_id,
                    cuenta_id=cuenta_id,
                    compania_id=compania_id,
                    usuario_id=usuario_id
                )
                resultados["tesoreria"] = resultados_tesoreria
                logger.info(f"✅ Tesorería procesada: {len(resultados_tesoreria)} actualizaciones")
            except Exception as e:
                logger.error(f"❌ Error procesando tesorería: {e}")
            
            # 2. PROCESAR PAGADURÍA (incluyendo cross-dependencies con tesorería)
            logger.info("📊 Procesando dependencias de PAGADURÍA...")
            try:
                resultados_pagaduria = self._procesar_dependencias_pagaduria(
                    fecha=fecha,
                    cuenta_id=cuenta_id,
                    compania_id=compania_id,
                    usuario_id=usuario_id
                )
                resultados["pagaduria"] = resultados_pagaduria
                logger.info(f"✅ Pagaduría procesada: {len(resultados_pagaduria)} actualizaciones")
            except Exception as e:
                logger.error(f"❌ Error procesando pagaduría: {e}")
            
            # 3. VERIFICAR CROSS-DEPENDENCIES ESPECÍFICAS
            logger.info("🔗 Verificando dependencias cruzadas...")
            cross_updates = self._procesar_dependencias_cruzadas(
                fecha=fecha,
                cuenta_id=cuenta_id,
                compania_id=compania_id,
                usuario_id=usuario_id
            )
            resultados["cross_dashboard"] = cross_updates
            
            total_actualizaciones = len(resultados["tesoreria"]) + len(resultados["pagaduria"]) + len(cross_updates)
            logger.info(f"🎉 Recálculo completo finalizado: {total_actualizaciones} actualizaciones totales")
            
            return resultados
            
        except Exception as e:
            logger.error(f"💥 Error en recálculo completo: {e}")
            return {"tesoreria": [], "pagaduria": [], "cross_dashboard": []}
    
    def _procesar_dependencias_cruzadas(
        self,
        fecha: date,
        cuenta_id: Optional[int] = None,
        compania_id: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Procesa dependencias específicas entre dashboards:
        - MOVIMIENTO TESORERIA (ID 84) = SUB-TOTAL TESORERÍA (ID 50)
        - Otras cross-dependencies futuras
        """
        try:
            actualizaciones = []
            
            # Obtener todas las cuentas si no se especifica una
            if cuenta_id:
                cuentas_ids = [cuenta_id]
            else:
                cuentas_ids = [cuenta.id for cuenta in self.db.query(CuentaBancaria).all()]
            
            # CROSS-DEPENDENCY: MOVIMIENTO TESORERIA = SUB-TOTAL TESORERÍA
            for cuenta in cuentas_ids:
                logger.info(f"🔗 Cross-dependency: MOVIMIENTO TESORERIA para cuenta {cuenta}")
                
                # Buscar SUB-TOTAL TESORERÍA (puede estar en tesorería o pagaduría)
                subtotal_tesoreria = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 50,  # SUB-TOTAL TESORERÍA
                    TransaccionFlujoCaja.cuenta_id == cuenta
                ).first()
                
                if subtotal_tesoreria:
                    monto_subtotal = subtotal_tesoreria.monto
                    area_origen = subtotal_tesoreria.area.value
                    
                    # Actualizar MOVIMIENTO TESORERIA en pagaduría
                    movimiento_tesoreria = self.db.query(TransaccionFlujoCaja).filter(
                        TransaccionFlujoCaja.fecha == fecha,
                        TransaccionFlujoCaja.concepto_id == 84,  # MOVIMIENTO TESORERIA
                        TransaccionFlujoCaja.cuenta_id == cuenta,
                        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                    ).first()
                    
                    if movimiento_tesoreria:
                        # Actualizar existente
                        monto_anterior = movimiento_tesoreria.monto
                        if monto_anterior != monto_subtotal:
                            movimiento_tesoreria.monto = monto_subtotal
                            movimiento_tesoreria.descripcion = f"Cross-update: SUB-TOTAL TESORERÍA ({area_origen})"
                            
                            # Actualizar auditoría
                            auditoria_actual = movimiento_tesoreria.auditoria or {}
                            auditoria_actual.update({
                                "accion": "cross_update_automatico",
                                "usuario_id": usuario_id or 1,
                                "timestamp": datetime.now().isoformat(),
                                "origen": {
                                    "concepto_id": 50,
                                    "area_origen": area_origen,
                                    "monto_anterior": float(monto_anterior),
                                    "monto_nuevo": float(monto_subtotal)
                                },
                                "tipo": "cross_dashboard_update"
                            })
                            movimiento_tesoreria.auditoria = auditoria_actual
                            
                            self.db.commit()
                            logger.info(f"🔄 Cross-update: MOVIMIENTO TESORERIA actualizado ${monto_anterior} → ${monto_subtotal}")
                            
                            actualizaciones.append({
                                "concepto_id": 84,
                                "concepto_nombre": "MOVIMIENTO TESORERIA",
                                "tipo": "cross_dashboard_update",
                                "monto_anterior": float(monto_anterior),
                                "monto_nuevo": float(monto_subtotal),
                                "origen_dashboard": area_origen,
                                "destino_dashboard": "pagaduria"
                            })
            
            # NUEVA CROSS-DEPENDENCY: VENTANILLA = SUBTOTAL MOVIMIENTO PAGADURIA
            logger.info("🏪 Procesando cross-dependency: VENTANILLA...")
            consumo_updates = self._procesar_ventanilla_automatico(
                fecha=fecha,
                cuenta_id=cuenta_id,
                compania_id=compania_id,
                usuario_id=usuario_id
            )
            actualizaciones.extend(consumo_updates)
            
            return actualizaciones
            
        except Exception as e:
            logger.error(f"❌ Error en dependencias cruzadas: {e}")
            return []

    def procesar_dependencias_avanzadas(
        self, 
        fecha: date, 
        area: AreaTransaccionSchema,
        concepto_modificado_id: Optional[int] = None,
        cuenta_id: Optional[int] = None,
        compania_id: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Procesa todas las dependencias avanzadas para una fecha y área específica.
        Incluye auto-cálculo del SALDO INICIAL basado en SALDO FINAL del día anterior.
        """
        try:
            actualizaciones = []
            
            # PRIMERO: Procesar auto-cálculo del SALDO INICIAL del día anterior
            # ⚠️ DESHABILITADO: Interfiere con proyecciones de días hábiles
            # saldo_inicial_updates = self._procesar_saldo_inicial_automatico(
            #     fecha=fecha,
            #     cuenta_id=cuenta_id,
            #     compania_id=compania_id,
            #     usuario_id=usuario_id or 1
            # )
            # actualizaciones.extend(saldo_inicial_updates)
            
            # SEGUNDO: Procesar dependencias normales
            conceptos_dependientes = self._obtener_conceptos_dependientes(area)
            
            for concepto in conceptos_dependientes:
                resultado = self._procesar_concepto_dependiente(
                    concepto=concepto,
                    fecha=fecha,
                    cuenta_id=cuenta_id,
                    compania_id=compania_id,
                    usuario_id=usuario_id or 1
                )
                
                if resultado:
                    actualizaciones.append(resultado)
            
            # TERCERO: Procesar dependencias específicas de pagaduría
            if area == AreaTransaccionSchema.pagaduria or area == 'PAGADURIA':
                # Para pagaduría, usar lógica específica en lugar de la general
                conceptos_pagaduria_especiales = [52]  # DIFERENCIA SALDOS
                conceptos_dependientes = [c for c in conceptos_dependientes 
                                        if c.id not in conceptos_pagaduria_especiales]
                
                pagaduria_updates = self._procesar_dependencias_pagaduria(
                    fecha=fecha,
                    cuenta_id=cuenta_id,
                    compania_id=compania_id,
                    usuario_id=usuario_id or 1
                )
                actualizaciones.extend(pagaduria_updates)
            
            self.db.commit()
            return actualizaciones
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error procesando dependencias: {str(e)}")
            raise
    
    def _obtener_conceptos_dependientes(self, area: AreaTransaccionSchema) -> List[ConceptoFlujoCaja]:
        """Obtiene todos los conceptos que tienen dependencias definidas."""
        if area == AreaTransaccionSchema.tesoreria or area == 'TESORERIA':
            area_concepto = AreaConcepto.tesoreria
        elif area == AreaTransaccionSchema.pagaduria or area == 'PAGADURIA':
            area_concepto = AreaConcepto.pagaduria
        else:
            area_concepto = AreaConcepto.tesoreria
        
        return self.db.query(ConceptoFlujoCaja).filter(
            or_(
                ConceptoFlujoCaja.depende_de_concepto_id.isnot(None),
                ConceptoFlujoCaja.formula_dependencia.isnot(None)
            ),
            ConceptoFlujoCaja.activo == True,
            or_(
                ConceptoFlujoCaja.area == area_concepto, 
                ConceptoFlujoCaja.area == AreaConcepto.ambas
            )
        ).all()

    def _procesar_concepto_dependiente(
        self,
        concepto: ConceptoFlujoCaja,
        fecha: date,
        concepto_modificado_id: Optional[int] = None,
        cuenta_id: Optional[int] = None,
        compania_id: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> Optional[Dict]:
        """Procesa un concepto dependiente específico."""
        try:
            area = AreaTransaccionSchema.tesoreria if concepto.area == AreaConcepto.tesoreria else AreaTransaccionSchema.pagaduria
            
            nuevo_monto = None
            
            if concepto.formula_dependencia:
                nuevo_monto = self._calcular_formula_compleja(concepto.formula_dependencia, fecha, area, cuenta_id)
                if nuevo_monto is None:
                    logger.warning(f"Fórmula no reconocida: {concepto.formula_dependencia}")
                    return None
            elif concepto.depende_de_concepto_id and concepto.tipo_dependencia:
                transaccion_base = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == concepto.depende_de_concepto_id,
                    TransaccionFlujoCaja.cuenta_id == cuenta_id,
                    TransaccionFlujoCaja.area == self._convertir_area_a_enum(area)
                ).first()
                
                if transaccion_base:
                    if concepto.tipo_dependencia == TipoDependencia.porcentaje:
                        porcentaje = 10
                        nuevo_monto = transaccion_base.monto * (Decimal(porcentaje) / 100)
                    else:
                        nuevo_monto = transaccion_base.monto
            
            if nuevo_monto is None:
                return None
            
            area_enum = self._convertir_area_a_enum(area)
            transaccion_existente = self.db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha,
                TransaccionFlujoCaja.concepto_id == concepto.id,
                TransaccionFlujoCaja.cuenta_id == cuenta_id,
                TransaccionFlujoCaja.area == area_enum
            ).first()
            
            if transaccion_existente:
                monto_anterior = transaccion_existente.monto
                transaccion_existente.monto = nuevo_monto
                transaccion_existente.descripcion = f"Actualizado automáticamente por dependencia"
                
                # Actualizar auditoría para transacción existente
                from datetime import datetime
                auditoria_actual = transaccion_existente.auditoria or {}
                auditoria_actual.update({
                    "ultima_modificacion": {
                        "accion": "actualizacion_automatica",
                        "usuario_id": usuario_id or 1,
                        "timestamp": datetime.now().isoformat(),
                        "monto_anterior": float(monto_anterior),
                        "monto_nuevo": float(nuevo_monto),
                        "formula": concepto.formula_dependencia,
                        "tipo": "dependencia_automatica"
                    }
                })
                transaccion_existente.auditoria = auditoria_actual
                transaccion = transaccion_existente
            else:
                transaccion = self._crear_o_actualizar_transaccion(
                    concepto_id=concepto.id,
                    fecha=fecha,
                    nuevo_monto=nuevo_monto,
                    cuenta_id=cuenta_id,
                    compania_id=compania_id,
                    area=area,
                    usuario_id=usuario_id or 1
                )
                monto_anterior = Decimal('0.00')
            
            return {
                'concepto_id': concepto.id,
                'concepto_nombre': concepto.nombre,
                'transaccion_id': transaccion.id if transaccion else None,
                'monto_anterior': monto_anterior,
                'monto_nuevo': nuevo_monto,
                'fecha': fecha,
                'area': area
            }
            
        except Exception as e:
            logger.error(f"Error procesando concepto {concepto.id}: {str(e)}")
            return None
    
    def _calcular_formula_compleja(self, formula: str, fecha: date, area: AreaTransaccionSchema, cuenta_id: int) -> Optional[Decimal]:
        """Calcula una fórmula compleja como SUMA(1,2,3) o RESTA(4,5) para una cuenta específica."""
        try:
            formula = formula.strip().upper()
            
            if formula.startswith('SUMA(') and formula.endswith(')'):
                conceptos_ids = self._extraer_ids_formula(formula)
                return self._calcular_suma_conceptos(conceptos_ids, fecha, area, cuenta_id)
            elif formula.startswith('RESTA(') and formula.endswith(')'):
                conceptos_ids = self._extraer_ids_formula(formula)
                return self._calcular_resta_conceptos(conceptos_ids, fecha, area, cuenta_id)
            else:
                logger.warning(f"Fórmula no soportada: {formula}")
                return None
                
        except Exception as e:
            logger.error(f"Error calculando fórmula {formula} para cuenta {cuenta_id}: {str(e)}")
            return None
    
    def _calcular_suma_conceptos(self, conceptos_ids: List[int], fecha: date, area: AreaTransaccionSchema, cuenta_id: int) -> Decimal:
        """Calcula la suma de varios conceptos para una cuenta específica."""
        total = Decimal('0.00')
        area_enum = self._convertir_area_a_enum(area)
        
        for concepto_id in conceptos_ids:
            transaccion = self.db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha,
                TransaccionFlujoCaja.concepto_id == concepto_id,
                TransaccionFlujoCaja.cuenta_id == cuenta_id,
                TransaccionFlujoCaja.area == area_enum
            ).first()
            
            if transaccion:
                total += transaccion.monto
                logger.debug(f"Cuenta {cuenta_id}, Concepto {concepto_id}: ${transaccion.monto} (Total acumulado: ${total})")
        
        logger.info(f"Suma total para cuenta {cuenta_id}, conceptos {conceptos_ids}: ${total}")
        return total
    
    def _calcular_resta_conceptos(self, conceptos_ids: List[int], fecha: date, area: AreaTransaccionSchema, cuenta_id: int) -> Decimal:
        """Calcula la resta de conceptos para una cuenta específica: primer concepto menos el resto."""
        if not conceptos_ids:
            return Decimal('0.00')
        
        area_enum = self._convertir_area_a_enum(area)
        resultado = Decimal('0.00')
        
        for i, concepto_id in enumerate(conceptos_ids):
            transaccion = self.db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha,
                TransaccionFlujoCaja.concepto_id == concepto_id,
                TransaccionFlujoCaja.cuenta_id == cuenta_id,
                TransaccionFlujoCaja.area == area_enum
            ).first()
            
            if transaccion:
                if i == 0:
                    resultado = transaccion.monto
                else:
                    resultado -= transaccion.monto
        
        return resultado
    
    def _extraer_ids_formula(self, formula: str) -> List[int]:
        """Extrae los IDs de una fórmula como SUMA(1,2,3)."""
        inicio = formula.find('(') + 1
        fin = formula.rfind(')')
        contenido = formula[inicio:fin]
        
        ids_str = contenido.split(',')
        return [int(id_str.strip()) for id_str in ids_str if id_str.strip().isdigit()]
    
    def _crear_o_actualizar_transaccion(
        self,
        concepto_id: int,
        fecha: date,
        nuevo_monto: Decimal,
        cuenta_id: Optional[int] = None,
        compania_id: Optional[int] = None,
        area: AreaTransaccionSchema = AreaTransaccionSchema.tesoreria,
        usuario_id: Optional[int] = None
    ) -> Optional[TransaccionFlujoCaja]:
        """Crea o actualiza una transacción para un concepto dependiente."""
        try:
            from datetime import datetime
            area_enum = self._convertir_area_a_enum(area)
            
            # Obtener información del concepto para la auditoría
            concepto = self.db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == concepto_id).first()
            
            transaccion = TransaccionFlujoCaja(
                fecha=fecha,
                concepto_id=concepto_id,
                cuenta_id=cuenta_id,
                monto=nuevo_monto,
                descripcion="Creado automáticamente por dependencia",
                usuario_id=usuario_id or 1,
                area=area_enum,
                compania_id=compania_id or 1,
                auditoria={
                    "accion": "creacion_automatica",
                    "usuario_id": usuario_id or 1,
                    "timestamp": datetime.now().isoformat(),
                    "monto_inicial": float(nuevo_monto),
                    "formula": concepto.formula_dependencia if concepto else None,
                    "tipo": "dependencia_automatica",
                    "concepto_nombre": concepto.nombre if concepto else "Desconocido"
                }
            )
            
            self.db.add(transaccion)
            return transaccion
            
        except Exception as e:
            logger.error(f"Error creando transacción para concepto {concepto_id}: {str(e)}")
            return None

    def _procesar_saldo_inicial_automatico(
        self,
        fecha: date,
        cuenta_id: Optional[int] = None,
        compania_id: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Procesa automáticamente el SALDO INICIAL del día actual
        basándose en el SALDO FINAL CUENTAS del día anterior.
        """
        try:
            actualizaciones = []
            fecha_anterior = fecha - timedelta(days=1)
            
            # ID del concepto SALDO INICIAL (basado en el análisis)
            SALDO_INICIAL_ID = 1
            SALDO_FINAL_CUENTAS_ID = 51
            
            # Obtener todas las cuentas si no se especifica una
            if cuenta_id:
                cuentas_a_procesar = [cuenta_id]
            else:
                # Obtener todas las cuentas que tienen SALDO FINAL del día anterior
                saldos_finales = self.db.query(TransaccionFlujoCaja.cuenta_id).filter(
                    TransaccionFlujoCaja.fecha == fecha_anterior,
                    TransaccionFlujoCaja.concepto_id == SALDO_FINAL_CUENTAS_ID,
                    TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
                ).distinct().all()
                cuentas_a_procesar = [saldo[0] for saldo in saldos_finales]
            
            logger.info(f"Procesando SALDO INICIAL para {len(cuentas_a_procesar)} cuentas en fecha {fecha}")
            
            for cuenta in cuentas_a_procesar:
                # Verificar si ya existe SALDO INICIAL para esta fecha y cuenta
                saldo_inicial_existente = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == SALDO_INICIAL_ID,
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
                ).first()
                
                if saldo_inicial_existente:
                    logger.info(f"SALDO INICIAL ya existe para cuenta {cuenta} en fecha {fecha}")
                    continue
                
                # Obtener SALDO FINAL del día anterior
                saldo_final_anterior = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha_anterior,
                    TransaccionFlujoCaja.concepto_id == SALDO_FINAL_CUENTAS_ID,
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
                ).first()
                
                if not saldo_final_anterior:
                    logger.info(f"No hay SALDO FINAL del día anterior para cuenta {cuenta}")
                    continue
                
                # Crear SALDO INICIAL con el valor del SALDO FINAL anterior
                monto_saldo_inicial = saldo_final_anterior.monto
                
                nueva_transaccion = self._crear_o_actualizar_transaccion(
                    concepto_id=SALDO_INICIAL_ID,
                    cuenta_id=cuenta,
                    fecha=fecha,
                    nuevo_monto=monto_saldo_inicial,
                    area=AreaTransaccionSchema.tesoreria,
                    compania_id=compania_id,
                    usuario_id=usuario_id
                )
                
                if nueva_transaccion:
                    # Modificar la auditoría para indicar que es SALDO INICIAL automático
                    nueva_transaccion.auditoria.update({
                        "tipo": "saldo_inicial_automatico",
                        "saldo_final_anterior": float(saldo_final_anterior.monto),
                        "fecha_anterior": fecha_anterior.isoformat(),
                        "concepto_nombre": "SALDO INICIAL"
                    })
                    
                    actualizaciones.append({
                        "concepto_id": SALDO_INICIAL_ID,
                        "concepto_nombre": "SALDO INICIAL",
                        "transaccion_id": nueva_transaccion.id,
                        "monto_anterior": Decimal('0.00'),
                        "monto_nuevo": monto_saldo_inicial,
                        "fecha": fecha,
                        "area": AreaTransaccionSchema.tesoreria,
                        "cuenta_id": cuenta
                    })
                    
                    logger.info(f"✅ SALDO INICIAL creado: Cuenta {cuenta}, Monto ${monto_saldo_inicial}")
            
            # Hacer commit de todas las transacciones creadas
            if actualizaciones:
                self.db.commit()
                logger.info(f"✅ {len(actualizaciones)} SALDO INICIAL guardados en base de datos")
            
            return actualizaciones
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error procesando SALDO INICIAL automático: {str(e)}")
            return []
    
    def _procesar_ventanilla_automatico(
        self,
        fecha: date,
        cuenta_id: Optional[int] = None,
        compania_id: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Procesa automáticamente CONSUMO (ID 2) del día actual
        basándose en SUBTOTAL MOVIMIENTO PAGADURIA (ID 82) del mismo día.
        """
        try:
            actualizaciones = []
            
            # Obtener todas las cuentas si no se especifica una
            if cuenta_id:
                cuentas_ids = [cuenta_id]
            else:
                cuentas_ids = [1, 2, 3, 4]  # IDs de cuentas existentes
            
            logger.info(f"�️ Procesando CONSUMO automático para fecha {fecha}")
            
            for cuenta in cuentas_ids:
                logger.info(f"📊 Procesando CONSUMO para cuenta {cuenta}...")
                
                # Buscar SUBTOTAL MOVIMIENTO PAGADURIA (ID 82) del mismo día
                subtotal_movimiento = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 82,  # SUBTOTAL MOVIMIENTO PAGADURIA
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).first()
                
                if subtotal_movimiento:
                    monto_subtotal = subtotal_movimiento.monto
                    
                    logger.info(f"💰 Cuenta {cuenta}: SUBTOTAL MOVIMIENTO PAGADURIA = ${monto_subtotal}")
                    
                    # Verificar si ya existe CONSUMO (ID 2) para este día
                    consumo_existente = self.db.query(TransaccionFlujoCaja).filter(
                        TransaccionFlujoCaja.fecha == fecha,
                        TransaccionFlujoCaja.concepto_id == 2,  # CONSUMO
                        TransaccionFlujoCaja.cuenta_id == cuenta,
                        TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
                    ).first()
                    
                    if consumo_existente:
                        # Actualizar existente
                        monto_anterior = consumo_existente.monto
                        consumo_existente.monto = monto_subtotal
                        consumo_existente.descripcion = "Auto-calculado: igual a SUBTOTAL MOVIMIENTO PAGADURIA"
                        
                        # Actualizar auditoría
                        auditoria_actual = consumo_existente.auditoria or {}
                        auditoria_actual.update({
                            "accion": "actualizacion_automatica",
                            "usuario_id": usuario_id or 1,
                            "timestamp": datetime.now().isoformat(),
                            "cambio": {
                                "monto_anterior": float(monto_anterior),
                                "monto_nuevo": float(monto_subtotal),
                                "origen": {
                                    "concepto_id": 82,
                                    "concepto_nombre": "SUBTOTAL MOVIMIENTO PAGADURIA",
                                    "fecha_origen": fecha.isoformat(),
                                    "monto_origen": float(monto_subtotal)
                                },
                                "formula": "CONSUMO = SUBTOTAL MOVIMIENTO PAGADURIA"
                            },
                            "tipo": "consumo_automatico"
                        })
                        consumo_existente.auditoria = auditoria_actual
                        
                        logger.info(f"✅ CONSUMO actualizado: Cuenta {cuenta}, ${monto_anterior} → ${monto_subtotal}")
                    else:
                        # Crear nueva transacción
                        nueva_transaccion_consumo = TransaccionFlujoCaja(
                            fecha=fecha,
                            concepto_id=2,  # CONSUMO
                            cuenta_id=cuenta,
                            monto=monto_subtotal,
                            descripcion="Auto-calculado: igual a SUBTOTAL MOVIMIENTO PAGADURIA",
                            usuario_id=usuario_id or 1,
                            area=AreaTransaccion.tesoreria,  # CONSUMO está en área tesorería
                            compania_id=compania_id or 1,
                            auditoria={
                                "accion": "creacion_automatica",
                                "usuario_id": usuario_id or 1,
                                "timestamp": datetime.now().isoformat(),
                                "origen": {
                                    "concepto_id": 82,
                                    "concepto_nombre": "SUBTOTAL MOVIMIENTO PAGADURIA",
                                    "fecha_origen": fecha.isoformat(),
                                    "monto_origen": float(monto_subtotal)
                                },
                                "formula": "CONSUMO = SUBTOTAL MOVIMIENTO PAGADURIA",
                                "monto_calculado": float(monto_subtotal),
                                "tipo": "consumo_automatico"
                            }
                        )
                        
                        self.db.add(nueva_transaccion_consumo)
                        logger.info(f"✅ CONSUMO creado: Cuenta {cuenta}, ${monto_subtotal}")
                    
                    actualizaciones.append({
                        "concepto_id": 2,
                        "concepto_nombre": "CONSUMO",
                        "monto_nuevo": monto_subtotal,
                        "fecha": fecha,
                        "area": AreaTransaccionSchema.tesoreria,
                        "cuenta_id": cuenta,
                        "origen": {
                            "concepto_id": 82,
                            "concepto_nombre": "SUBTOTAL MOVIMIENTO PAGADURIA",
                            "monto_origen": float(monto_subtotal)
                        }
                    })
                else:
                    logger.info(f"⚠️ No se encontró SUBTOTAL MOVIMIENTO PAGADURIA (ID 82) para fecha {fecha}, cuenta {cuenta}")
            
            # Commit de todas las actualizaciones
            if actualizaciones:
                self.db.commit()
                logger.info(f"✅ {len(actualizaciones)} VENTANILLA procesados y guardados")
            
            return actualizaciones
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error procesando VENTANILLA automático: {str(e)}")
            return []

    def _procesar_dependencias_pagaduria(
        self,
        fecha: date,
        concepto_modificado_id: Optional[int] = None,
        cuenta_id: Optional[int] = None,
        compania_id: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Procesa dependencias específicas de pagaduría
        Especialmente para DIFERENCIA SALDOS = SALDOS EN BANCOS + SALDO DIA ANTERIOR
        """
        try:
            actualizaciones = []
            
            # Obtener todas las cuentas si no se especifica una
            if cuenta_id is None:
                cuentas = self.db.query(CuentaBancaria).all()
                cuentas_ids = [cuenta.id for cuenta in cuentas]
            else:
                cuentas_ids = [cuenta_id]
            
            logger.info(f"🔄 Procesando dependencias pagaduría para {len(cuentas_ids)} cuentas")
            
            for cuenta in cuentas_ids:
                # Verificar si existen los conceptos base (53 y 54)
                saldos_bancos = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 53,  # SALDOS EN BANCOS
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).first()
                
                saldo_anterior = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 54,  # SALDO DIA ANTERIOR
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).first()
                
                # SIEMPRE calcular DIFERENCIA SALDOS = SALDOS EN BANCOS - SALDO DIA ANTERIOR
                # (incluso si uno o ambos valores no existen, se tratan como 0)
                monto_saldos_bancos = saldos_bancos.monto if saldos_bancos else Decimal('0.00')
                monto_saldo_anterior = saldo_anterior.monto if saldo_anterior else Decimal('0.00')
                
                diferencia_saldos = monto_saldos_bancos - monto_saldo_anterior
                
                logger.info(f"📊 Cuenta {cuenta}: SALDOS BANCOS=${monto_saldos_bancos} - SALDO ANTERIOR=${monto_saldo_anterior} = DIFERENCIA=${diferencia_saldos}")
                
                # Crear o actualizar DIFERENCIA SALDOS (ID 52)
                transaccion_diferencia = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 52,  # DIFERENCIA SALDOS
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).first()
                
                if transaccion_diferencia:
                    # Actualizar existente
                    monto_anterior = transaccion_diferencia.monto
                    transaccion_diferencia.monto = diferencia_saldos
                    transaccion_diferencia.descripcion = "Auto-calculado: SALDOS BANCOS - SALDO ANTERIOR"
                    
                    logger.info(f"✅ DIFERENCIA SALDOS actualizada: Cuenta {cuenta}, ${monto_anterior} → ${diferencia_saldos}")
                else:
                    # Crear nueva
                    nueva_transaccion = TransaccionFlujoCaja(
                        fecha=fecha,
                        concepto_id=52,  # DIFERENCIA SALDOS
                        cuenta_id=cuenta,
                        monto=diferencia_saldos,
                        descripcion="Auto-calculado: SALDOS BANCOS - SALDO ANTERIOR",
                        usuario_id=usuario_id or 1,
                        area=AreaTransaccion.pagaduria,
                        compania_id=compania_id or 1,
                        auditoria={
                            "accion": "creacion_automatica",
                            "usuario_id": usuario_id or 1,
                            "timestamp": datetime.now().isoformat(),
                            "formula": "RESTA(53,54)",
                            "componentes": {
                                "saldos_bancos_id53": float(monto_saldos_bancos),
                                "saldo_anterior_id54": float(monto_saldo_anterior)
                            },
                            "tipo": "dependencia_pagaduria"
                        }
                    )
                    
                    self.db.add(nueva_transaccion)
                    logger.info(f"✅ DIFERENCIA SALDOS creada: Cuenta {cuenta}, ${diferencia_saldos}")
                
                actualizaciones.append({
                        "concepto_id": 52,
                        "concepto_nombre": "DIFERENCIA SALDOS",
                        "monto_nuevo": diferencia_saldos,
                        "fecha": fecha,
                        "area": AreaTransaccionSchema.pagaduria,
                        "cuenta_id": cuenta,
                        "componentes": {
                            "saldos_bancos": monto_saldos_bancos,
                            "saldo_anterior": monto_saldo_anterior
                        }
                    })
            
            # LÓGICA: SALDO DIA ANTERIOR = SALDO TOTAL EN BANCOS del día anterior
            for cuenta in cuentas_ids:
                # Calcular fecha anterior
                fecha_anterior = fecha - timedelta(days=1)
                
                # Buscar SALDO TOTAL EN BANCOS (ID 85) del día anterior
                saldo_total_anterior = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha_anterior,
                    TransaccionFlujoCaja.concepto_id == 85,  # SALDO TOTAL EN BANCOS
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).first()
                
                if saldo_total_anterior:
                    monto_saldo_total = saldo_total_anterior.monto
                    
                    logger.info(f"📊 Cuenta {cuenta}: SALDO TOTAL BANCOS {fecha_anterior}=${monto_saldo_total}")
                    
                    # Verificar si ya existe SALDO DIA ANTERIOR para hoy
                    saldo_dia_anterior = self.db.query(TransaccionFlujoCaja).filter(
                        TransaccionFlujoCaja.fecha == fecha,
                        TransaccionFlujoCaja.concepto_id == 54,  # SALDO DIA ANTERIOR
                        TransaccionFlujoCaja.cuenta_id == cuenta,
                        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                    ).first()
                    
                    if saldo_dia_anterior:
                        # Actualizar existente
                        monto_anterior_saldo = saldo_dia_anterior.monto
                        saldo_dia_anterior.monto = monto_saldo_total
                        saldo_dia_anterior.descripcion = f"Auto-calculado: SALDO TOTAL BANCOS del {fecha_anterior}"
                        
                        logger.info(f"✅ SALDO DIA ANTERIOR actualizado: Cuenta {cuenta}, ${monto_anterior_saldo} → ${monto_saldo_total}")
                    else:
                        # Crear nueva transacción
                        nueva_transaccion_saldo = TransaccionFlujoCaja(
                            fecha=fecha,
                            concepto_id=54,  # SALDO DIA ANTERIOR
                            cuenta_id=cuenta,
                            monto=monto_saldo_total,
                            descripcion=f"Auto-calculado: SALDO TOTAL BANCOS del {fecha_anterior}",
                            usuario_id=usuario_id or 1,
                            area=AreaTransaccion.pagaduria,
                            compania_id=compania_id or 1,
                            auditoria={
                                "accion": "creacion_automatica",
                                "usuario_id": usuario_id or 1,
                                "timestamp": datetime.now().isoformat(),
                                "origen": {
                                    "concepto_origen_id": 85,
                                    "concepto_origen_nombre": "SALDO TOTAL EN BANCOS",
                                    "fecha_origen": fecha_anterior.isoformat(),
                                    "monto_origen": float(monto_saldo_total)
                                },
                                "tipo": "saldo_dia_anterior_automatico"
                            }
                        )
                        
                        self.db.add(nueva_transaccion_saldo)
                        logger.info(f"✅ SALDO DIA ANTERIOR creado: Cuenta {cuenta}, ${monto_saldo_total} (del {fecha_anterior})")
                    
                    actualizaciones.append({
                        "concepto_id": 54,
                        "concepto_nombre": "SALDO DIA ANTERIOR",
                        "monto_nuevo": monto_saldo_total,
                        "fecha": fecha,
                        "area": AreaTransaccionSchema.pagaduria,
                        "cuenta_id": cuenta,
                        "origen": {
                            "fecha_anterior": fecha_anterior,
                            "saldo_total_bancos": monto_saldo_total
                        }
                    })
                else:
                    logger.info(f"⚠️ No se encontró SALDO TOTAL EN BANCOS para {fecha_anterior}, cuenta {cuenta}")
            
            # NUEVA LÓGICA: SUBTOTAL MOVIMIENTO PAGADURIA (ID 82) = SUMA de conceptos 55-81
            for cuenta in cuentas_ids:
                # IDs de los conceptos que forman el subtotal movimiento (55-81)
                conceptos_movimiento = list(range(55, 82))  # 55, 56, 57, ..., 81
                
                logger.info(f"📊 Calculando SUBTOTAL MOVIMIENTO para cuenta {cuenta}...")
                
                # Obtener todas las transacciones de estos conceptos para esta fecha y cuenta
                # INCLUIR información del concepto para conocer el código (I/E/N)
                transacciones_movimiento = self.db.query(TransaccionFlujoCaja, ConceptoFlujoCaja).join(
                    ConceptoFlujoCaja, TransaccionFlujoCaja.concepto_id == ConceptoFlujoCaja.id
                ).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id.in_(conceptos_movimiento),
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).all()
                
                # Calcular la suma total respetando los códigos I/E/N
                subtotal_movimiento = Decimal('0.00')
                conceptos_incluidos = []
                
                for transaccion, concepto in transacciones_movimiento:
                    # Determinar el signo según el código del concepto
                    monto_original = transaccion.monto
                    
                    if concepto.codigo == 'E':  # Egreso - debe ser negativo
                        monto_calculado = -abs(monto_original)  # Asegurar que sea negativo
                        signo = "(-)"
                    elif concepto.codigo == 'I':  # Ingreso - debe ser positivo
                        monto_calculado = abs(monto_original)   # Asegurar que sea positivo
                        signo = "(+)"
                    elif concepto.codigo == 'N':  # Neutral - debe ser positivo
                        monto_calculado = abs(monto_original)   # Asegurar que sea positivo
                        signo = "(+)"
                    else:  # Sin código definido - mantener el monto original
                        monto_calculado = monto_original
                        signo = "(?)"
                    
                    subtotal_movimiento += monto_calculado
                    conceptos_incluidos.append({
                        "concepto_id": transaccion.concepto_id,
                        "concepto_nombre": concepto.nombre,
                        "codigo": concepto.codigo,
                        "monto_original": float(monto_original),
                        "monto_calculado": float(monto_calculado),
                        "signo": signo
                    })
                    
                    logger.info(f"  • [{transaccion.concepto_id}] {concepto.nombre} ({concepto.codigo}): ${monto_original} → ${monto_calculado} {signo}")
                
                logger.info(f"💰 Cuenta {cuenta}: SUBTOTAL MOVIMIENTO = ${subtotal_movimiento} ({len(conceptos_incluidos)} conceptos)")
                
                # Verificar si ya existe SUBTOTAL MOVIMIENTO PAGADURIA (ID 82)
                subtotal_existente = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 82,  # SUBTOTAL MOVIMIENTO PAGADURIA
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).first()
                
                if subtotal_existente:
                    # Actualizar existente
                    monto_anterior = subtotal_existente.monto
                    subtotal_existente.monto = subtotal_movimiento
                    subtotal_existente.descripcion = f"Auto-calculado: I(+) E(-) N(+) de {len(conceptos_incluidos)} conceptos"
                    
                    # Actualizar auditoría
                    auditoria_actual = subtotal_existente.auditoria or {}
                    auditoria_actual.update({
                        "accion": "actualizacion_automatica",
                        "usuario_id": usuario_id or 1,
                        "timestamp": datetime.now().isoformat(),
                        "cambio": {
                            "monto_anterior": float(monto_anterior),
                            "monto_nuevo": float(subtotal_movimiento),
                            "conceptos_incluidos": conceptos_incluidos,
                            "formula": "SUMA respetando códigos: I(+), E(-), N(+)"
                        },
                        "tipo": "subtotal_movimiento_automatico"
                    })
                    subtotal_existente.auditoria = auditoria_actual
                    
                    logger.info(f"✅ SUBTOTAL MOVIMIENTO actualizado: Cuenta {cuenta}, ${monto_anterior} → ${subtotal_movimiento}")
                else:
                    # Crear nueva transacción
                    nueva_transaccion_subtotal = TransaccionFlujoCaja(
                        fecha=fecha,
                        concepto_id=82,  # SUBTOTAL MOVIMIENTO PAGADURIA
                        cuenta_id=cuenta,
                        monto=subtotal_movimiento,
                        descripcion=f"Auto-calculado: I(+) E(-) N(+) de {len(conceptos_incluidos)} conceptos",
                        usuario_id=usuario_id or 1,
                        area=AreaTransaccion.pagaduria,
                        compania_id=compania_id or 1,
                        auditoria={
                            "accion": "creacion_automatica",
                            "usuario_id": usuario_id or 1,
                            "timestamp": datetime.now().isoformat(),
                            "conceptos_incluidos": conceptos_incluidos,
                            "formula": "SUMA respetando códigos: I(+), E(-), N(+)",
                            "total_conceptos": len(conceptos_incluidos),
                            "monto_calculado": float(subtotal_movimiento),
                            "tipo": "subtotal_movimiento_automatico"
                        }
                    )
                    
                    self.db.add(nueva_transaccion_subtotal)
                    logger.info(f"✅ SUBTOTAL MOVIMIENTO creado: Cuenta {cuenta}, ${subtotal_movimiento}")
                
                # Solo agregar a actualizaciones si hay conceptos incluidos
                if conceptos_incluidos:
                    actualizaciones.append({
                        "concepto_id": 82,
                        "concepto_nombre": "SUBTOTAL MOVIMIENTO PAGADURIA",
                        "monto_nuevo": subtotal_movimiento,
                        "fecha": fecha,
                        "area": AreaTransaccionSchema.pagaduria,
                        "cuenta_id": cuenta,
                        "conceptos_incluidos": conceptos_incluidos,
                        "total_conceptos": len(conceptos_incluidos),
                        "formula_aplicada": "I(+), E(-), N(+)"
                    })
            
            # NUEVA LÓGICA: SUBTOTAL SALDO INICIAL PAGADURIA (ID 83) = SUBTOTAL MOVIMIENTO (ID 82) + SALDO DIA ANTERIOR (ID 54)
            for cuenta in cuentas_ids:
                logger.info(f"📊 Calculando SUBTOTAL SALDO INICIAL para cuenta {cuenta}...")
                
                # Buscar SUBTOTAL MOVIMIENTO PAGADURIA (ID 82)
                subtotal_movimiento_trans = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 82,  # SUBTOTAL MOVIMIENTO PAGADURIA
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).first()
                
                # Buscar SALDO DIA ANTERIOR (ID 54)
                saldo_dia_anterior_trans = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 54,  # SALDO DIA ANTERIOR
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).first()
                
                # Solo calcular si al menos uno de los componentes existe
                monto_subtotal_movimiento = subtotal_movimiento_trans.monto if subtotal_movimiento_trans else Decimal('0.00')
                monto_saldo_anterior = saldo_dia_anterior_trans.monto if saldo_dia_anterior_trans else Decimal('0.00')
                
                if subtotal_movimiento_trans or saldo_dia_anterior_trans:
                    subtotal_saldo_inicial = monto_subtotal_movimiento + monto_saldo_anterior
                    
                    componentes_presentes = []
                    if subtotal_movimiento_trans:
                        componentes_presentes.append(f"SUBTOTAL MOVIMIENTO: ${monto_subtotal_movimiento}")
                    if saldo_dia_anterior_trans:
                        componentes_presentes.append(f"SALDO DIA ANTERIOR: ${monto_saldo_anterior}")
                    
                    logger.info(f"💰 Cuenta {cuenta}: SUBTOTAL SALDO INICIAL = ${subtotal_saldo_inicial} ({', '.join(componentes_presentes)})")
                    
                    # Verificar si ya existe SUBTOTAL SALDO INICIAL PAGADURIA (ID 83)
                    subtotal_saldo_inicial_existente = self.db.query(TransaccionFlujoCaja).filter(
                        TransaccionFlujoCaja.fecha == fecha,
                        TransaccionFlujoCaja.concepto_id == 83,  # SUBTOTAL SALDO INICIAL PAGADURIA
                        TransaccionFlujoCaja.cuenta_id == cuenta,
                        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                    ).first()
                    
                    if subtotal_saldo_inicial_existente:
                        # Actualizar existente
                        monto_anterior = subtotal_saldo_inicial_existente.monto
                        subtotal_saldo_inicial_existente.monto = subtotal_saldo_inicial
                        subtotal_saldo_inicial_existente.descripcion = f"Auto-calculado: ${monto_subtotal_movimiento} + ${monto_saldo_anterior} (parcial: {len(componentes_presentes)}/2)"
                        
                        # Actualizar auditoría
                        auditoria_actual = subtotal_saldo_inicial_existente.auditoria or {}
                        auditoria_actual.update({
                            "accion": "actualizacion_automatica",
                            "usuario_id": usuario_id or 1,
                            "timestamp": datetime.now().isoformat(),
                            "cambio": {
                                "monto_anterior": float(monto_anterior),
                                "monto_nuevo": float(subtotal_saldo_inicial),
                                "componentes_disponibles": len(componentes_presentes),
                                "componentes_total": 2,
                                "componentes": {
                                    "subtotal_movimiento_id82": float(monto_subtotal_movimiento),
                                    "saldo_dia_anterior_id54": float(monto_saldo_anterior)
                                },
                                "formula": "ID82 + ID54 (cálculo parcial permitido)"
                            },
                            "tipo": "subtotal_saldo_inicial_automatico"
                        })
                        subtotal_saldo_inicial_existente.auditoria = auditoria_actual
                        
                        logger.info(f"✅ SUBTOTAL SALDO INICIAL actualizado: Cuenta {cuenta}, ${monto_anterior} → ${subtotal_saldo_inicial}")
                    else:
                        # Crear nueva transacción
                        nueva_transaccion_saldo_inicial = TransaccionFlujoCaja(
                            fecha=fecha,
                            concepto_id=83,  # SUBTOTAL SALDO INICIAL PAGADURIA
                            cuenta_id=cuenta,
                            monto=subtotal_saldo_inicial,
                            descripcion="Auto-calculado: SUBTOTAL MOVIMIENTO + SALDO DIA ANTERIOR",
                            usuario_id=usuario_id or 1,
                            area=AreaTransaccion.pagaduria,
                            compania_id=compania_id or 1,
                            auditoria={
                                "accion": "creacion_automatica",
                                "usuario_id": usuario_id or 1,
                                "timestamp": datetime.now().isoformat(),
                                "componentes": {
                                    "subtotal_movimiento_id82": float(monto_subtotal_movimiento),
                                    "saldo_dia_anterior_id54": float(monto_saldo_anterior)
                                },
                                "formula": "ID82 + ID54",
                                "monto_calculado": float(subtotal_saldo_inicial),
                                "tipo": "subtotal_saldo_inicial_automatico"
                            }
                        )
                        
                        self.db.add(nueva_transaccion_saldo_inicial)
                        logger.info(f"✅ SUBTOTAL SALDO INICIAL creado: Cuenta {cuenta}, ${subtotal_saldo_inicial}")
                    
                    actualizaciones.append({
                        "concepto_id": 83,
                        "concepto_nombre": "SUBTOTAL SALDO INICIAL PAGADURIA",
                        "monto_nuevo": subtotal_saldo_inicial,
                        "fecha": fecha,
                        "area": AreaTransaccionSchema.pagaduria,
                        "cuenta_id": cuenta,
                        "componentes": {
                            "subtotal_movimiento": float(monto_subtotal_movimiento),
                            "saldo_dia_anterior": float(monto_saldo_anterior)
                        }
                    })
                else:
                    # Log de componentes faltantes
                    componentes_faltantes = []
                    if not subtotal_movimiento_trans:
                        componentes_faltantes.append("SUBTOTAL MOVIMIENTO (ID 82)")
                    if not saldo_dia_anterior_trans:
                        componentes_faltantes.append("SALDO DIA ANTERIOR (ID 54)")
                    
                    logger.info(f"⚠️ No se puede calcular SUBTOTAL SALDO INICIAL para cuenta {cuenta}. Faltan: {', '.join(componentes_faltantes)}")
            
            # NUEVA LÓGICA: MOVIMIENTO TESORERIA (ID 84) = SUB-TOTAL TESORERÍA (ID 50)
            for cuenta in cuentas_ids:
                logger.info(f"📊 Calculando MOVIMIENTO TESORERIA para cuenta {cuenta}...")
                
                # Buscar SUB-TOTAL TESORERÍA (ID 50) del mismo día
                # Nota: SUB-TOTAL TESORERÍA puede estar en área 'tesoreria', verificamos ambas áreas
                subtotal_tesoreria = None
                
                # Primero buscar en área tesorería
                subtotal_tesoreria = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 50,  # SUB-TOTAL TESORERÍA
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
                ).first()
                
                # Si no se encuentra en tesorería, buscar en pagaduría
                if not subtotal_tesoreria:
                    subtotal_tesoreria = self.db.query(TransaccionFlujoCaja).filter(
                        TransaccionFlujoCaja.fecha == fecha,
                        TransaccionFlujoCaja.concepto_id == 50,  # SUB-TOTAL TESORERÍA
                        TransaccionFlujoCaja.cuenta_id == cuenta,
                        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                    ).first()
                
                if subtotal_tesoreria:
                    monto_subtotal_tesoreria = subtotal_tesoreria.monto
                    area_origen = subtotal_tesoreria.area.value
                    
                    logger.info(f"💰 Cuenta {cuenta}: SUB-TOTAL TESORERÍA (área {area_origen}) = ${monto_subtotal_tesoreria}")
                    
                    # Verificar si ya existe MOVIMIENTO TESORERIA (ID 84) en pagaduría
                    movimiento_tesoreria_existente = self.db.query(TransaccionFlujoCaja).filter(
                        TransaccionFlujoCaja.fecha == fecha,
                        TransaccionFlujoCaja.concepto_id == 84,  # MOVIMIENTO TESORERIA
                        TransaccionFlujoCaja.cuenta_id == cuenta,
                        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                    ).first()
                    
                    if movimiento_tesoreria_existente:
                        # Actualizar existente
                        monto_anterior = movimiento_tesoreria_existente.monto
                        movimiento_tesoreria_existente.monto = monto_subtotal_tesoreria
                        movimiento_tesoreria_existente.descripcion = f"Auto-calculado: igual a SUB-TOTAL TESORERÍA (área {area_origen})"
                        
                        # Actualizar auditoría
                        auditoria_actual = movimiento_tesoreria_existente.auditoria or {}
                        auditoria_actual.update({
                            "accion": "actualizacion_automatica",
                            "usuario_id": usuario_id or 1,
                            "timestamp": datetime.now().isoformat(),
                            "cambio": {
                                "monto_anterior": float(monto_anterior),
                                "monto_nuevo": float(monto_subtotal_tesoreria),
                                "origen": {
                                    "concepto_id": 50,
                                    "concepto_nombre": "SUB-TOTAL TESORERÍA",
                                    "area_origen": area_origen,
                                    "monto_origen": float(monto_subtotal_tesoreria)
                                },
                                "formula": "MOVIMIENTO TESORERIA = SUB-TOTAL TESORERÍA"
                            },
                            "tipo": "movimiento_tesoreria_automatico"
                        })
                        movimiento_tesoreria_existente.auditoria = auditoria_actual
                        
                        logger.info(f"✅ MOVIMIENTO TESORERIA actualizado: Cuenta {cuenta}, ${monto_anterior} → ${monto_subtotal_tesoreria}")
                    else:
                        # Crear nueva transacción
                        nueva_transaccion_movimiento = TransaccionFlujoCaja(
                            fecha=fecha,
                            concepto_id=84,  # MOVIMIENTO TESORERIA
                            cuenta_id=cuenta,
                            monto=monto_subtotal_tesoreria,
                            descripcion=f"Auto-calculado: igual a SUB-TOTAL TESORERÍA (área {area_origen})",
                            usuario_id=usuario_id or 1,
                            area=AreaTransaccion.pagaduria,
                            compania_id=compania_id or 1,
                            auditoria={
                                "accion": "creacion_automatica",
                                "usuario_id": usuario_id or 1,
                                "timestamp": datetime.now().isoformat(),
                                "origen": {
                                    "concepto_id": 50,
                                    "concepto_nombre": "SUB-TOTAL TESORERÍA",
                                    "area_origen": area_origen,
                                    "monto_origen": float(monto_subtotal_tesoreria)
                                },
                                "formula": "MOVIMIENTO TESORERIA = SUB-TOTAL TESORERÍA",
                                "monto_calculado": float(monto_subtotal_tesoreria),
                                "tipo": "movimiento_tesoreria_automatico"
                            }
                        )
                        
                        self.db.add(nueva_transaccion_movimiento)
                        logger.info(f"✅ MOVIMIENTO TESORERIA creado: Cuenta {cuenta}, ${monto_subtotal_tesoreria}")
                    
                    actualizaciones.append({
                        "concepto_id": 84,
                        "concepto_nombre": "MOVIMIENTO TESORERIA",
                        "monto_nuevo": monto_subtotal_tesoreria,
                        "fecha": fecha,
                        "area": AreaTransaccionSchema.pagaduria,
                        "cuenta_id": cuenta,
                        "origen": {
                            "concepto_id": 50,
                            "concepto_nombre": "SUB-TOTAL TESORERÍA",
                            "area_origen": area_origen,
                            "monto_origen": float(monto_subtotal_tesoreria)
                        }
                    })
                else:
                    logger.info(f"⚠️ No se encontró SUB-TOTAL TESORERÍA (ID 50) para fecha {fecha}, cuenta {cuenta}")
            
            # NUEVA LÓGICA: SALDO TOTAL EN BANCOS (ID 85) = SUBTOTAL SALDO INICIAL PAGADURIA (ID 83) + MOVIMIENTO TESORERIA (ID 84)
            for cuenta in cuentas_ids:
                logger.info(f"📊 Calculando SALDO TOTAL EN BANCOS para cuenta {cuenta}...")
                
                # Buscar SUBTOTAL SALDO INICIAL PAGADURIA (ID 83)
                subtotal_saldo_inicial = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 83,  # SUBTOTAL SALDO INICIAL PAGADURIA
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).first()
                
                # Buscar MOVIMIENTO TESORERIA (ID 84)
                movimiento_tesoreria = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 84,  # MOVIMIENTO TESORERIA
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).first()
                
                # Calcular con valores disponibles (0 si no existen)
                monto_subtotal_saldo = subtotal_saldo_inicial.monto if subtotal_saldo_inicial else Decimal('0.00')
                monto_movimiento_tesoreria = movimiento_tesoreria.monto if movimiento_tesoreria else Decimal('0.00')
                
                # Solo calcular si al menos uno de los componentes existe
                if subtotal_saldo_inicial or movimiento_tesoreria:
                    saldo_total_bancos = monto_subtotal_saldo + monto_movimiento_tesoreria
                    
                    componentes_presentes = []
                    if subtotal_saldo_inicial:
                        componentes_presentes.append(f"SUBTOTAL SALDO INICIAL: ${monto_subtotal_saldo}")
                    if movimiento_tesoreria:
                        componentes_presentes.append(f"MOVIMIENTO TESORERIA: ${monto_movimiento_tesoreria}")
                    
                    logger.info(f"💰 Cuenta {cuenta}: SALDO TOTAL BANCOS = ${saldo_total_bancos} ({', '.join(componentes_presentes)})")
                    
                    # Verificar si ya existe SALDO TOTAL EN BANCOS (ID 85)
                    saldo_total_existente = self.db.query(TransaccionFlujoCaja).filter(
                        TransaccionFlujoCaja.fecha == fecha,
                        TransaccionFlujoCaja.concepto_id == 85,  # SALDO TOTAL EN BANCOS
                        TransaccionFlujoCaja.cuenta_id == cuenta,
                        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                    ).first()
                    
                    if saldo_total_existente:
                        # Actualizar existente
                        monto_anterior = saldo_total_existente.monto
                        saldo_total_existente.monto = saldo_total_bancos
                        saldo_total_existente.descripcion = f"Auto-calculado: ${monto_subtotal_saldo} + ${monto_movimiento_tesoreria} (parcial: {len(componentes_presentes)}/2)"
                        
                        # Actualizar auditoría
                        auditoria_actual = saldo_total_existente.auditoria or {}
                        auditoria_actual.update({
                            "accion": "actualizacion_automatica",
                            "usuario_id": usuario_id or 1,
                            "timestamp": datetime.now().isoformat(),
                            "cambio": {
                                "monto_anterior": float(monto_anterior),
                                "monto_nuevo": float(saldo_total_bancos),
                                "componentes_disponibles": len(componentes_presentes),
                                "componentes_total": 2,
                                "componentes": {
                                    "subtotal_saldo_inicial_id83": float(monto_subtotal_saldo),
                                    "movimiento_tesoreria_id84": float(monto_movimiento_tesoreria)
                                },
                                "formula": "ID83 + ID84 (cálculo parcial permitido)"
                            },
                            "tipo": "saldo_total_bancos_automatico"
                        })
                        saldo_total_existente.auditoria = auditoria_actual
                        
                        logger.info(f"✅ SALDO TOTAL EN BANCOS actualizado: Cuenta {cuenta}, ${monto_anterior} → ${saldo_total_bancos}")
                        
                        # 🚀 LÓGICA PROACTIVA: Proyectar SALDO TOTAL EN BANCOS actualizado → SALDO DÍA ANTERIOR del próximo día hábil
                        try:
                            # Usar días hábiles para proyección inteligente
                            fecha_siguiente = self.dias_habiles_service.proximo_dia_habil(fecha, incluir_fecha_actual=False)
                            
                            # Verificar si ya existe SALDO DÍA ANTERIOR para el día siguiente
                            saldo_dia_siguiente = self.db.query(TransaccionFlujoCaja).filter(
                                TransaccionFlujoCaja.fecha == fecha_siguiente,
                                TransaccionFlujoCaja.concepto_id == 54,  # SALDO DÍA ANTERIOR
                                TransaccionFlujoCaja.cuenta_id == cuenta,
                                TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                            ).first()
                            
                            if saldo_dia_siguiente:
                                # Actualizar proyección existente
                                monto_anterior_proyectado = saldo_dia_siguiente.monto
                                saldo_dia_siguiente.monto = saldo_total_bancos
                                saldo_dia_siguiente.descripcion = f"Auto-calculado: SALDO TOTAL BANCOS del {fecha} (próximo día hábil)"
                                
                                logger.info(f"🔄 PROYECCIÓN ACTUALIZADA (días hábiles): SALDO DÍA ANTERIOR del {fecha_siguiente}: ${monto_anterior_proyectado} → ${saldo_total_bancos}")
                            else:
                                # Crear nueva proyección
                                nueva_proyeccion = TransaccionFlujoCaja(
                                    fecha=fecha_siguiente,
                                    concepto_id=54,  # SALDO DÍA ANTERIOR
                                    cuenta_id=cuenta,
                                    monto=saldo_total_bancos,
                                    descripcion=f"Auto-calculado: SALDO TOTAL BANCOS del {fecha} (próximo día hábil)",
                                    usuario_id=usuario_id or 1,
                                    area=AreaTransaccion.pagaduria,
                                    compania_id=compania_id or 1,
                                    auditoria={
                                        "accion": "proyeccion_automatica_update",
                                        "usuario_id": usuario_id or 1,
                                        "timestamp": datetime.now().isoformat(),
                                        "origen": {
                                            "concepto_origen_id": 85,
                                            "concepto_origen_nombre": "SALDO TOTAL EN BANCOS",
                                            "fecha_origen": fecha.isoformat(),
                                            "monto_origen": float(saldo_total_bancos)
                                        },
                                        "tipo": "proyeccion_saldo_dia_anterior_update"
                                    }
                                )
                                
                                self.db.add(nueva_proyeccion)
                                logger.info(f"🚀 PROYECCIÓN CREADA (días hábiles): SALDO DÍA ANTERIOR para {fecha_siguiente}: ${saldo_total_bancos}")
                        except Exception as e:
                            logger.warning(f"⚠️ Error en proyección al actualizar SALDO TOTAL EN BANCOS: {e}")
                        
                        monto_anterior = saldo_total_existente.monto
                        saldo_total_existente.monto = saldo_total_bancos
                        saldo_total_existente.descripcion = "Auto-calculado: SUBTOTAL SALDO INICIAL + MOVIMIENTO TESORERIA"
                        
                        # Actualizar auditoría
                        auditoria_actual = saldo_total_existente.auditoria or {}
                        auditoria_actual.update({
                            "accion": "actualizacion_automatica",
                            "usuario_id": usuario_id or 1,
                            "timestamp": datetime.now().isoformat(),
                            "cambio": {
                                "monto_anterior": float(monto_anterior),
                                "monto_nuevo": float(saldo_total_bancos),
                                "componentes": {
                                    "subtotal_saldo_inicial_id83": float(monto_subtotal_saldo),
                                    "movimiento_tesoreria_id84": float(monto_movimiento_tesoreria)
                                },
                                "formula": "SALDO TOTAL BANCOS = SUBTOTAL SALDO INICIAL + MOVIMIENTO TESORERIA"
                            },
                            "tipo": "saldo_total_bancos_automatico"
                        })
                        saldo_total_existente.auditoria = auditoria_actual
                        
                        logger.info(f"✅ SALDO TOTAL EN BANCOS actualizado: Cuenta {cuenta}, ${monto_anterior} → ${saldo_total_bancos}")
                    else:
                        # Crear nueva transacción
                        nueva_transaccion_saldo_total = TransaccionFlujoCaja(
                            fecha=fecha,
                            concepto_id=85,  # SALDO TOTAL EN BANCOS
                            cuenta_id=cuenta,
                            monto=saldo_total_bancos,
                            descripcion="Auto-calculado: SUBTOTAL SALDO INICIAL + MOVIMIENTO TESORERIA",
                            usuario_id=usuario_id or 1,
                            area=AreaTransaccion.pagaduria,
                            compania_id=compania_id or 1,
                            auditoria={
                                "accion": "creacion_automatica",
                                "usuario_id": usuario_id or 1,
                                "timestamp": datetime.now().isoformat(),
                                "componentes": {
                                    "subtotal_saldo_inicial_id83": float(monto_subtotal_saldo),
                                    "movimiento_tesoreria_id84": float(monto_movimiento_tesoreria)
                                },
                                "formula": "SALDO TOTAL BANCOS = SUBTOTAL SALDO INICIAL + MOVIMIENTO TESORERIA",
                                "monto_calculado": float(saldo_total_bancos),
                                "tipo": "saldo_total_bancos_automatico"
                            }
                        )
                        
                        self.db.add(nueva_transaccion_saldo_total)
                        logger.info(f"✅ SALDO TOTAL EN BANCOS creado: Cuenta {cuenta}, ${saldo_total_bancos}")
                    
                    # 🚀 LÓGICA PROACTIVA: Proyectar SALDO TOTAL EN BANCOS del día actual → SALDO DÍA ANTERIOR del próximo día hábil
                    try:
                        # Usar días hábiles para proyección inteligente
                        fecha_siguiente = self.dias_habiles_service.proximo_dia_habil(fecha, incluir_fecha_actual=False)
                        
                        # Verificar si ya existe SALDO DÍA ANTERIOR para el día siguiente
                        saldo_dia_siguiente = self.db.query(TransaccionFlujoCaja).filter(
                            TransaccionFlujoCaja.fecha == fecha_siguiente,
                            TransaccionFlujoCaja.concepto_id == 54,  # SALDO DÍA ANTERIOR
                            TransaccionFlujoCaja.cuenta_id == cuenta,
                            TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                        ).first()
                        
                        if saldo_dia_siguiente:
                            # Actualizar existente
                            monto_anterior_proyectado = saldo_dia_siguiente.monto
                            saldo_dia_siguiente.monto = saldo_total_bancos
                            saldo_dia_siguiente.descripcion = f"Auto-calculado: SALDO TOTAL BANCOS del {fecha} (próximo día hábil)"
                            
                            logger.info(f"🔄 PROYECCIÓN (días hábiles): SALDO DÍA ANTERIOR del {fecha_siguiente} actualizado: ${monto_anterior_proyectado} → ${saldo_total_bancos}")
                        else:
                            # Crear nueva proyección para el día siguiente
                            nueva_proyeccion = TransaccionFlujoCaja(
                                fecha=fecha_siguiente,
                                concepto_id=54,  # SALDO DÍA ANTERIOR
                                cuenta_id=cuenta,
                                monto=saldo_total_bancos,
                                descripcion=f"Auto-calculado: SALDO TOTAL BANCOS del {fecha} (próximo día hábil)",
                                usuario_id=usuario_id or 1,
                                area=AreaTransaccion.pagaduria,
                                compania_id=compania_id or 1,
                                auditoria={
                                    "accion": "proyeccion_automatica",
                                    "usuario_id": usuario_id or 1,
                                    "timestamp": datetime.now().isoformat(),
                                    "origen": {
                                        "concepto_origen_id": 85,
                                        "concepto_origen_nombre": "SALDO TOTAL EN BANCOS",
                                        "fecha_origen": fecha.isoformat(),
                                        "monto_origen": float(saldo_total_bancos)
                                    },
                                    "tipo": "proyeccion_saldo_dia_anterior"
                                }
                            )
                            
                            self.db.add(nueva_proyeccion)
                            logger.info(f"🚀 PROYECCIÓN (días hábiles): SALDO DÍA ANTERIOR creado para {fecha_siguiente}: ${saldo_total_bancos}")
                    except Exception as e:
                        logger.warning(f"⚠️ Error en proyección SALDO DÍA ANTERIOR: {e}")
                    
                    actualizaciones.append({
                        "concepto_id": 85,
                        "concepto_nombre": "SALDO TOTAL EN BANCOS",
                        "monto_nuevo": saldo_total_bancos,
                        "fecha": fecha,
                        "area": AreaTransaccionSchema.pagaduria,
                        "cuenta_id": cuenta,
                        "componentes": {
                            "subtotal_saldo_inicial": float(monto_subtotal_saldo),
                            "movimiento_tesoreria": float(monto_movimiento_tesoreria)
                        }
                    })
                else:
                    # Log de componentes faltantes
                    componentes_faltantes = []
                    if not subtotal_saldo_inicial:
                        componentes_faltantes.append("SUBTOTAL SALDO INICIAL PAGADURIA (ID 83)")
                    if not movimiento_tesoreria:
                        componentes_faltantes.append("MOVIMIENTO TESORERIA (ID 84)")
                    
                    logger.info(f"⚠️ No se puede calcular SALDO TOTAL EN BANCOS para cuenta {cuenta}. Faltan: {', '.join(componentes_faltantes)}")
            
            # 🚀 NUEVA LÓGICA: PROYECCIÓN PARA TESORERÍA
            # SALDO FINAL CUENTAS (ID 51) → SALDO INICIAL (ID 1) del próximo día hábil
            for cuenta in cuentas_ids:
                # Buscar SALDO FINAL CUENTAS del día actual en área tesorería
                saldo_final_cuentas = self.db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha,
                    TransaccionFlujoCaja.concepto_id == 51,  # SALDO FINAL CUENTAS
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
                ).first()
                
                if saldo_final_cuentas and saldo_final_cuentas.monto != 0:
                    try:
                        # 🔍 DEBUG: Capturar el valor ANTES de usarlo
                        monto_original = saldo_final_cuentas.monto
                        logger.info(f"🔍 DEBUG PROYECCIÓN TESORERÍA - Cuenta {cuenta}: Monto leído = ${monto_original}")
                        
                        # Usar días hábiles para proyección inteligente
                        fecha_siguiente = self.dias_habiles_service.proximo_dia_habil(fecha, incluir_fecha_actual=False)
                        
                        # Verificar si ya existe SALDO INICIAL para el día siguiente
                        saldo_inicial_siguiente = self.db.query(TransaccionFlujoCaja).filter(
                            TransaccionFlujoCaja.fecha == fecha_siguiente,
                            TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
                            TransaccionFlujoCaja.cuenta_id == cuenta,
                            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
                        ).first()
                        
                        # 🔍 DEBUG: Verificar que el monto no cambió
                        monto_antes_asignar = saldo_final_cuentas.monto
                        logger.info(f"🔍 DEBUG PROYECCIÓN TESORERÍA - Cuenta {cuenta}: Monto antes de asignar = ${monto_antes_asignar}")
                        
                        if saldo_inicial_siguiente:
                            # Actualizar proyección existente
                            monto_anterior_proyectado = saldo_inicial_siguiente.monto
                            saldo_inicial_siguiente.monto = monto_original  # Usar el valor capturado
                            saldo_inicial_siguiente.descripcion = f"Auto-calculado: SALDO FINAL CUENTAS del {fecha} (próximo día hábil)"
                            
                            logger.info(f"🔄 PROYECCIÓN TESORERÍA (días hábiles): SALDO INICIAL del {fecha_siguiente} actualizado: ${monto_anterior_proyectado} → ${monto_original}")
                        else:
                            # Crear nueva proyección para el día siguiente
                            nueva_proyeccion = TransaccionFlujoCaja(
                                fecha=fecha_siguiente,
                                concepto_id=1,  # SALDO INICIAL
                                cuenta_id=cuenta,
                                monto=monto_original,  # Usar el valor capturado
                                descripcion=f"Auto-calculado: SALDO FINAL CUENTAS del {fecha} (próximo día hábil)",
                                usuario_id=usuario_id or 1,
                                area=AreaTransaccion.tesoreria,
                                compania_id=compania_id or 1,
                                auditoria={
                                    "accion": "proyeccion_automatica_tesoreria",
                                    "usuario_id": usuario_id or 1,
                                    "timestamp": datetime.now().isoformat(),
                                    "origen": {
                                        "concepto_origen_id": 51,
                                        "concepto_origen_nombre": "SALDO FINAL CUENTAS",
                                        "fecha_origen": fecha.isoformat(),
                                        "monto_origen": float(monto_original)  # Usar el valor capturado
                                    },
                                    "destino": {
                                        "concepto_destino_id": 1,
                                        "concepto_destino_nombre": "SALDO INICIAL",
                                        "fecha_destino": fecha_siguiente.isoformat()
                                    },
                                    "tipo": "proyeccion_dias_habiles_tesoreria"
                                }
                            )
                            
                            self.db.add(nueva_proyeccion)
                            logger.info(f"🚀 PROYECCIÓN TESORERÍA (días hábiles): SALDO INICIAL creado para {fecha_siguiente}: ${monto_original}")
                            
                    except Exception as e:
                        logger.error(f"❌ Error en proyección de tesorería para cuenta {cuenta}: {e}")
            
            # Commit de todas las actualizaciones
            if actualizaciones:
                self.db.commit()
                logger.info(f"✅ {len(actualizaciones)} dependencias de pagaduría procesadas y guardadas")
                
                # 🔥 TRIGGER AUTOMÁTICO: Si se actualizó SUBTOTAL MOVIMIENTO PAGADURIA (ID 82), 
                # disparar inmediatamente la sincronización de VENTANILLA (ID 3)
                subtotal_movimiento_actualizado = any(
                    update.get("concepto_id") == 82 for update in actualizaciones
                )
                
                if subtotal_movimiento_actualizado:
                    logger.info("�️ TRIGGER: SUBTOTAL MOVIMIENTO actualizado → Sincronizando CONSUMO...")
                    try:
                        consumo_updates = self._procesar_ventanilla_automatico(
                            fecha=fecha,
                            cuenta_id=cuenta_id,  # Usar el cuenta_id específico si se proporcionó
                            compania_id=compania_id,
                            usuario_id=usuario_id
                        )
                        
                        if consumo_updates:
                            logger.info(f"✅ CONSUMO sincronizado automáticamente: {len(consumo_updates)} actualizaciones")
                            # Agregar las actualizaciones de CONSUMO a la respuesta
                            for consumo_update in consumo_updates:
                                consumo_update["tipo_trigger"] = "auto_sync_from_subtotal_movimiento"
                            actualizaciones.extend(consumo_updates)
                        else:
                            logger.info("ℹ️ CONSUMO: No requiere actualización")
                            
                    except Exception as e:
                        logger.error(f"❌ Error sincronizando CONSUMO automáticamente: {e}")
            
            return actualizaciones
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error procesando dependencias pagaduría: {str(e)}")
            return []