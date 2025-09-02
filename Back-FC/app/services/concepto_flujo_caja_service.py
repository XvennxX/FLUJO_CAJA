"""
Servicios para el manejo de conceptos de flujo de caja
Lógica de negocio para CRUD y dependencias automáticas
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date
from decimal import Decimal

from ..models import ConceptoFlujoCaja, TransaccionFlujoCaja, AreaConcepto, TipoMovimiento, TipoDependencia
from ..schemas.flujo_caja import (
    ConceptoFlujoCajaCreate, 
    ConceptoFlujoCajaUpdate, 
    ConceptoFlujoCajaResponse,
    AreaConceptoSchema
)

class ConceptoFlujoCajaService:
    """Servicio para gestión de conceptos de flujo de caja"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def crear_concepto(self, concepto_data: ConceptoFlujoCajaCreate) -> ConceptoFlujoCaja:
        """Crear un nuevo concepto de flujo de caja"""
        
        # Validar dependencia si existe
        if concepto_data.depende_de_concepto_id:
            concepto_dependiente = self.obtener_concepto_por_id(concepto_data.depende_de_concepto_id)
            if not concepto_dependiente:
                raise ValueError(f"El concepto dependiente ID {concepto_data.depende_de_concepto_id} no existe")
            
            # Validar que no se cree una dependencia circular
            if self._validar_dependencia_circular(concepto_data.depende_de_concepto_id, None):
                raise ValueError("La dependencia crearía un ciclo circular")
        
        # Determinar el siguiente orden_display si no se especifica
        if concepto_data.orden_display == 0:
            max_orden = self.db.query(ConceptoFlujoCaja).filter(
                ConceptoFlujoCaja.area == concepto_data.area
            ).order_by(ConceptoFlujoCaja.orden_display.desc()).first()
            concepto_data.orden_display = (max_orden.orden_display + 1) if max_orden else 1
        
        # Crear el concepto
        db_concepto = ConceptoFlujoCaja(**concepto_data.dict())
        self.db.add(db_concepto)
        self.db.commit()
        self.db.refresh(db_concepto)
        
        return db_concepto
    
    def obtener_conceptos_por_area(self, area: AreaConceptoSchema, activos_only: bool = True) -> List[ConceptoFlujoCaja]:
        """Obtener conceptos por área, ordenados por orden_display"""
        query = self.db.query(ConceptoFlujoCaja)
        
        if area != AreaConceptoSchema.ambas:
            query = query.filter(or_(
                ConceptoFlujoCaja.area == area,
                ConceptoFlujoCaja.area == AreaConcepto.ambas
            ))
        
        if activos_only:
            query = query.filter(ConceptoFlujoCaja.activo == True)
        
        return query.order_by(ConceptoFlujoCaja.orden_display, ConceptoFlujoCaja.nombre).all()
    
    def obtener_concepto_por_id(self, concepto_id: int) -> Optional[ConceptoFlujoCaja]:
        """Obtener concepto por ID"""
        return self.db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == concepto_id).first()
    
    def actualizar_concepto(self, concepto_id: int, concepto_data: ConceptoFlujoCajaUpdate) -> Optional[ConceptoFlujoCaja]:
        """Actualizar un concepto existente"""
        db_concepto = self.obtener_concepto_por_id(concepto_id)
        if not db_concepto:
            return None
        
        # Validar dependencia si se está actualizando
        if concepto_data.depende_de_concepto_id is not None:
            if concepto_data.depende_de_concepto_id != db_concepto.depende_de_concepto_id:
                concepto_dependiente = self.obtener_concepto_por_id(concepto_data.depende_de_concepto_id)
                if not concepto_dependiente:
                    raise ValueError(f"El concepto dependiente ID {concepto_data.depende_de_concepto_id} no existe")
                
                # Validar dependencia circular
                if self._validar_dependencia_circular(concepto_data.depende_de_concepto_id, concepto_id):
                    raise ValueError("La dependencia crearía un ciclo circular")
        
        # Actualizar campos
        update_data = concepto_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_concepto, field, value)
        
        self.db.commit()
        self.db.refresh(db_concepto)
        return db_concepto
    
    def eliminar_concepto(self, concepto_id: int) -> bool:
        """Eliminar un concepto (soft delete - marcar como inactivo)"""
        db_concepto = self.obtener_concepto_por_id(concepto_id)
        if not db_concepto:
            return False
        
        # Verificar si tiene transacciones asociadas
        tiene_transacciones = self.db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == concepto_id
        ).first() is not None
        
        if tiene_transacciones:
            # Soft delete - marcar como inactivo
            db_concepto.activo = False
            self.db.commit()
        else:
            # Hard delete si no tiene transacciones
            self.db.delete(db_concepto)
            self.db.commit()
        
        return True
    
    def obtener_conceptos_con_dependencias(self, area: AreaConceptoSchema) -> List[ConceptoFlujoCaja]:
        """Obtener conceptos que tienen dependencias configuradas"""
        query = self.db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.depende_de_concepto_id.isnot(None),
            ConceptoFlujoCaja.activo == True
        )
        
        if area != AreaConceptoSchema.ambas:
            query = query.filter(or_(
                ConceptoFlujoCaja.area == area,
                ConceptoFlujoCaja.area == AreaConcepto.ambas
            ))
        
        return query.all()
    
    def reordenar_conceptos(self, area: AreaConceptoSchema, conceptos_ordenados: List[int]) -> bool:
        """Reordenar conceptos según una lista de IDs"""
        try:
            for orden, concepto_id in enumerate(conceptos_ordenados, 1):
                self.db.query(ConceptoFlujoCaja).filter(
                    ConceptoFlujoCaja.id == concepto_id,
                    or_(ConceptoFlujoCaja.area == area, ConceptoFlujoCaja.area == AreaConcepto.ambas)
                ).update({"orden_display": orden})
            
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def buscar_conceptos(self, termino: str, area: Optional[AreaConceptoSchema] = None) -> List[ConceptoFlujoCaja]:
        """Buscar conceptos por nombre o código"""
        query = self.db.query(ConceptoFlujoCaja).filter(
            or_(
                ConceptoFlujoCaja.nombre.ilike(f"%{termino}%"),
                ConceptoFlujoCaja.codigo.ilike(f"%{termino}%")
            ),
            ConceptoFlujoCaja.activo == True
        )
        
        if area:
            query = query.filter(or_(
                ConceptoFlujoCaja.area == area,
                ConceptoFlujoCaja.area == AreaConcepto.ambas
            ))
        
        return query.order_by(ConceptoFlujoCaja.orden_display).all()
    
    def obtener_estadisticas_conceptos(self) -> Dict[str, Any]:
        """Obtener estadísticas de conceptos"""
        total = self.db.query(ConceptoFlujoCaja).count()
        activos = self.db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.activo == True).count()
        
        por_area = {}
        for area in AreaConcepto:
            count = self.db.query(ConceptoFlujoCaja).filter(
                ConceptoFlujoCaja.area == area,
                ConceptoFlujoCaja.activo == True
            ).count()
            por_area[area.value] = count
        
        con_dependencias = self.db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.depende_de_concepto_id.isnot(None),
            ConceptoFlujoCaja.activo == True
        ).count()
        
        return {
            "total": total,
            "activos": activos,
            "inactivos": total - activos,
            "por_area": por_area,
            "con_dependencias": con_dependencias
        }
    
    def _validar_dependencia_circular(self, depende_de_id: int, concepto_actual_id: Optional[int] = None) -> bool:
        """Validar que no exista dependencia circular"""
        visitados = set()
        
        def buscar_ciclo(concepto_id: int) -> bool:
            if concepto_id in visitados:
                return True
            
            if concepto_id == concepto_actual_id:
                return True
            
            visitados.add(concepto_id)
            
            concepto = self.obtener_concepto_por_id(concepto_id)
            if concepto and concepto.depende_de_concepto_id:
                return buscar_ciclo(concepto.depende_de_concepto_id)
            
            return False
        
        return buscar_ciclo(depende_de_id)
