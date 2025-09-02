"""
Servicios para el manejo de transacciones de flujo de caja
Lógica de negocio para CRUD, cálculos automáticos y reportes
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from datetime import date, datetime
from decimal import Decimal

from ..models import (
    ConceptoFlujoCaja, TransaccionFlujoCaja, CuentaBancaria, Usuario,
    AreaConcepto, AreaTransaccion, TipoMovimiento, TipoDependencia
)
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

class TransaccionFlujoCajaService:
    """Servicio para gestión de transacciones de flujo de caja"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def crear_transaccion(self, transaccion_data: TransaccionFlujoCajaCreate, usuario_id: int) -> TransaccionFlujoCaja:
        """Crear una nueva transacción de flujo de caja"""
        
        # Validar que el concepto existe y está activo
        concepto = self.db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.id == transaccion_data.concepto_id,
            ConceptoFlujoCaja.activo == True
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
        
        # Crear la transacción
        db_transaccion = TransaccionFlujoCaja(
            **transaccion_data.dict(),
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
        
        # Procesar dependencias automáticas
        self._procesar_dependencias_automaticas(transaccion_data.fecha, transaccion_data.area, usuario_id)
        
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
        
        # Guardar valores originales para auditoría
        valores_originales = {
            "fecha": db_transaccion.fecha,
            "concepto_id": db_transaccion.concepto_id,
            "cuenta_id": db_transaccion.cuenta_id,
            "monto": str(db_transaccion.monto),
            "descripcion": db_transaccion.descripcion
        }
        
        # Actualizar campos
        update_data = transaccion_data.dict(exclude_unset=True)
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
        
        # Procesar dependencias automáticas si cambió la fecha o área
        if 'fecha' in update_data or 'area' in update_data:
            fecha_procesar = update_data.get('fecha', db_transaccion.fecha)
            area_procesar = update_data.get('area', db_transaccion.area)
            self._procesar_dependencias_automaticas(fecha_procesar, area_procesar, usuario_id)
        
        return db_transaccion
    
    def eliminar_transaccion(self, transaccion_id: int, usuario_id: int) -> bool:
        """Eliminar una transacción"""
        db_transaccion = self.obtener_transaccion_por_id(transaccion_id)
        if not db_transaccion:
            return False
        
        fecha = db_transaccion.fecha
        area = db_transaccion.area
        
        self.db.delete(db_transaccion)
        self.db.commit()
        
        # Procesar dependencias automáticas después de eliminar
        self._procesar_dependencias_automaticas(fecha, area, usuario_id)
        
        return True
    
    def obtener_flujo_caja_diario(self, fecha: date, area: AreaConceptoSchema) -> FlujoCajaDiarioResponse:
        """Obtener el flujo de caja completo de un día específico"""
        
        # Obtener conceptos del área ordenados
        conceptos_query = self.db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.activo == True
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
            ConceptoFlujoCaja.activo == True,
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
