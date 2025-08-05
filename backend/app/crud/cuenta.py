"""
CRUD para el modelo Cuenta
Operaciones específicas para gestión de cuentas
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.base import CRUDBase
from app.models.cuenta import Cuenta


class CRUDCuenta(CRUDBase[Cuenta, Dict[str, Any], Dict[str, Any]]):
    """CRUD operations para Cuenta"""
    
    def get_by_id(self, db: Session, *, id: int) -> Optional[Cuenta]:
        """Obtener cuenta por ID"""
        return db.query(Cuenta).filter(Cuenta.id_cuenta == id).first()
    
    def get_active_accounts(self, db: Session) -> List[Cuenta]:
        """Obtener cuentas activas"""
        return db.query(Cuenta).filter(Cuenta.estado == True).all()
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Cuenta]:
        """Obtener cuenta por nombre"""
        return db.query(Cuenta).filter(Cuenta.nombre == name).first()
    
    def update_balance(self, db: Session, *, account_id: int, amount: Decimal, operation: str) -> bool:
        """Actualizar saldo de cuenta"""
        try:
            cuenta = self.get_by_id(db, id=account_id)
            if not cuenta:
                return False
            
            if operation == "ADD":
                cuenta.saldo_actual += amount
            elif operation == "SUBTRACT":
                if cuenta.saldo_actual >= amount:
                    cuenta.saldo_actual -= amount
                else:
                    return False  # Saldo insuficiente
            
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
    
    def get_total_balance(self, db: Session) -> Decimal:
        """Obtener saldo total de todas las cuentas activas"""
        result = db.query(func.sum(Cuenta.saldo_actual)).filter(
            Cuenta.estado == True
        ).scalar()
        return result or Decimal('0.00')
    
    def get_accounts_summary(self, db: Session) -> Dict[str, Any]:
        """Obtener resumen de cuentas"""
        total_accounts = db.query(Cuenta).count()
        active_accounts = db.query(Cuenta).filter(Cuenta.estado == True).count()
        total_balance = self.get_total_balance(db)
        
        return {
            "total_cuentas": total_accounts,
            "cuentas_activas": active_accounts,
            "saldo_total": float(total_balance)
        }


# Instancia global del CRUD
cuenta = CRUDCuenta(Cuenta)
