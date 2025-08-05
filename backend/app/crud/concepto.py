"""
CRUD para el modelo Concepto
Operaciones específicas para gestión de conceptos
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.concepto import Concepto, TipoConcepto


class CRUDConcepto(CRUDBase[Concepto, Dict[str, Any], Dict[str, Any]]):
    """CRUD operations para Concepto"""
    
    def get_by_id(self, db: Session, *, id: int) -> Optional[Concepto]:
        """Obtener concepto por ID"""
        return db.query(Concepto).filter(Concepto.id_concepto == id).first()
    
    def get_by_type(self, db: Session, *, tipo: TipoConcepto) -> List[Concepto]:
        """Obtener conceptos por tipo (INGRESO/EGRESO)"""
        return db.query(Concepto).filter(Concepto.tipo == tipo).all()
    
    def get_income_concepts(self, db: Session) -> List[Concepto]:
        """Obtener conceptos de ingreso"""
        return self.get_by_type(db, tipo=TipoConcepto.INGRESO)
    
    def get_expense_concepts(self, db: Session) -> List[Concepto]:
        """Obtener conceptos de egreso"""
        return self.get_by_type(db, tipo=TipoConcepto.EGRESO)
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Concepto]:
        """Obtener concepto por nombre"""
        return db.query(Concepto).filter(Concepto.nombre == name).first()
    
    def create_concept(self, db: Session, *, nombre: str, tipo: TipoConcepto) -> Concepto:
        """Crear nuevo concepto"""
        db_obj = Concepto(
            nombre=nombre,
            tipo=tipo
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Instancia global del CRUD
concepto = CRUDConcepto(Concepto)
