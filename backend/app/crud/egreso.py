"""
CRUD para el modelo Egreso
Operaciones específicas para gestión de egresos
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.crud.base import CRUDBase
from app.models.egreso import Egreso
from app.schemas.transaction import EgresoCreate, EgresoUpdate


class CRUDEgreso(CRUDBase[Egreso, EgresoCreate, EgresoUpdate]):
    """CRUD operations para Egreso"""
    
    def get_by_id(self, db: Session, *, id: int) -> Optional[Egreso]:
        """Obtener egreso por ID"""
        return db.query(Egreso).filter(Egreso.id_egreso == id).first()
    
    def get_by_date_range(
        self, 
        db: Session, 
        *, 
        start_date: date, 
        end_date: date,
        account_id: Optional[int] = None
    ) -> List[Egreso]:
        """Obtener egresos por rango de fechas"""
        query = db.query(Egreso).filter(
            and_(
                Egreso.fecha >= start_date,
                Egreso.fecha <= end_date
            )
        )
        
        if account_id:
            query = query.filter(Egreso.id_cuenta == account_id)
        
        return query.order_by(desc(Egreso.fecha)).all()
    
    def get_by_account(self, db: Session, *, account_id: int) -> List[Egreso]:
        """Obtener egresos por cuenta"""
        return db.query(Egreso).filter(Egreso.id_cuenta == account_id).all()
    
    def get_by_concept(self, db: Session, *, concept_id: int) -> List[Egreso]:
        """Obtener egresos por concepto"""
        return db.query(Egreso).filter(Egreso.id_concepto == concept_id).all()
    
    def get_total_by_date(self, db: Session, *, fecha: date) -> Decimal:
        """Obtener total de egresos por fecha"""
        result = db.query(func.sum(Egreso.valor)).filter(
            func.date(Egreso.fecha) == fecha
        ).scalar()
        return result or Decimal('0.00')
    
    def get_total_by_month(self, db: Session, *, year: int, month: int) -> Decimal:
        """Obtener total de egresos por mes"""
        result = db.query(func.sum(Egreso.valor)).filter(
            and_(
                func.year(Egreso.fecha) == year,
                func.month(Egreso.fecha) == month
            )
        ).scalar()
        return result or Decimal('0.00')
    
    def get_recent_expenses(self, db: Session, *, limit: int = 10) -> List[Egreso]:
        """Obtener egresos recientes"""
        return db.query(Egreso).order_by(
            desc(Egreso.fecha)
        ).limit(limit).all()
    
    def get_expense_stats(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de egresos"""
        today = date.today()
        
        # Total hoy
        total_today = self.get_total_by_date(db, fecha=today)
        
        # Total este mes
        total_month = self.get_total_by_month(db, year=today.year, month=today.month)
        
        # Cantidad de egresos hoy
        count_today = db.query(Egreso).filter(
            func.date(Egreso.fecha) == today
        ).count()
        
        return {
            "total_hoy": float(total_today),
            "total_mes": float(total_month),
            "cantidad_hoy": count_today
        }


# Instancia global del CRUD
egreso = CRUDEgreso(Egreso)
