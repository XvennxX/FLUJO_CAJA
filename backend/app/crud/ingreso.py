"""
CRUD para el modelo Ingreso
Operaciones específicas para gestión de ingresos
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.crud.base import CRUDBase
from app.models.ingreso import Ingreso
from app.schemas.transaction import IngresoCreate, IngresoUpdate


class CRUDIngreso(CRUDBase[Ingreso, IngresoCreate, IngresoUpdate]):
    """CRUD operations para Ingreso"""
    
    def get_by_id(self, db: Session, *, id: int) -> Optional[Ingreso]:
        """Obtener ingreso por ID"""
        return db.query(Ingreso).filter(Ingreso.id_ingreso == id).first()
    
    def get_by_date_range(
        self, 
        db: Session, 
        *, 
        start_date: date, 
        end_date: date,
        account_id: Optional[int] = None
    ) -> List[Ingreso]:
        """Obtener ingresos por rango de fechas"""
        query = db.query(Ingreso).filter(
            and_(
                Ingreso.fecha >= start_date,
                Ingreso.fecha <= end_date
            )
        )
        
        if account_id:
            query = query.filter(Ingreso.id_cuenta == account_id)
        
        return query.order_by(desc(Ingreso.fecha)).all()
    
    def get_by_account(self, db: Session, *, account_id: int) -> List[Ingreso]:
        """Obtener ingresos por cuenta"""
        return db.query(Ingreso).filter(Ingreso.id_cuenta == account_id).all()
    
    def get_by_concept(self, db: Session, *, concept_id: int) -> List[Ingreso]:
        """Obtener ingresos por concepto"""
        return db.query(Ingreso).filter(Ingreso.id_concepto == concept_id).all()
    
    def get_total_by_date(self, db: Session, *, fecha: date) -> Decimal:
        """Obtener total de ingresos por fecha"""
        result = db.query(func.sum(Ingreso.valor)).filter(
            func.date(Ingreso.fecha) == fecha
        ).scalar()
        return result or Decimal('0.00')
    
    def get_total_by_month(self, db: Session, *, year: int, month: int) -> Decimal:
        """Obtener total de ingresos por mes"""
        result = db.query(func.sum(Ingreso.valor)).filter(
            and_(
                func.year(Ingreso.fecha) == year,
                func.month(Ingreso.fecha) == month
            )
        ).scalar()
        return result or Decimal('0.00')
    
    def get_recent_incomes(self, db: Session, *, limit: int = 10) -> List[Ingreso]:
        """Obtener ingresos recientes"""
        return db.query(Ingreso).order_by(
            desc(Ingreso.fecha)
        ).limit(limit).all()
    
    def get_income_stats(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de ingresos"""
        today = date.today()
        
        # Total hoy
        total_today = self.get_total_by_date(db, fecha=today)
        
        # Total este mes
        total_month = self.get_total_by_month(db, year=today.year, month=today.month)
        
        # Cantidad de ingresos hoy
        count_today = db.query(Ingreso).filter(
            func.date(Ingreso.fecha) == today
        ).count()
        
        return {
            "total_hoy": float(total_today),
            "total_mes": float(total_month),
            "cantidad_hoy": count_today
        }


# Instancia global del CRUD
ingreso = CRUDIngreso(Ingreso)
