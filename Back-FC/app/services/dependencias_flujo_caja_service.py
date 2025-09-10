"""
Servicio avanzado para el manejo de dependencias entre conceptos de flujo de caja.
Soporta múltiples conceptos, cálculos complejos y notificaciones en tiempo real.
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from app.models.conceptos_flujo_caja import ConceptoFlujoCaja, TipoDependencia, AreaConcepto
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.schemas.flujo_caja import AreaTransaccionSchema

logger = logging.getLogger(__name__)

class DependenciasFlujoCajaService:
    """
    Servicio especializado para manejar dependencias complejas entre conceptos.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def _convertir_area_a_enum(self, area: AreaTransaccionSchema) -> AreaTransaccion:
        """Convierte área de transacción schema a enum de base de datos"""
        if area == AreaTransaccionSchema.tesoreria or area == 'TESORERIA':
            return AreaTransaccion.tesoreria
        elif area == AreaTransaccionSchema.pagaduria or area == 'PAGADURIA':
            return AreaTransaccion.pagaduria
        else:
            return AreaTransaccion.tesoreria  # Default
    
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
            saldo_inicial_updates = self._procesar_saldo_inicial_automatico(
                fecha=fecha,
                cuenta_id=cuenta_id,
                compania_id=compania_id,
                usuario_id=usuario_id or 1
            )
            actualizaciones.extend(saldo_inicial_updates)
            
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