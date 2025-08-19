from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from ..models.companias import Compania
from ..schemas.companies import CompaniaCreate, CompaniaUpdate

class CompaniaService:
    """
    Servicio para lógica de negocio relacionada con compañías
    """
    
    @staticmethod
    def get_companies_with_stats(db: Session) -> List[Dict[str, Any]]:
        """
        Obtener compañías con estadísticas adicionales
        """
        from ..models.cuentas_bancarias import CuentaBancaria
        
        companies_with_stats = db.query(
            Compania.id,
            Compania.nombre,
            func.count(CuentaBancaria.id).label('total_cuentas')
        ).outerjoin(
            CuentaBancaria, Compania.id == CuentaBancaria.compania_id
        ).group_by(
            Compania.id, Compania.nombre
        ).all()
        
        return [
            {
                "id": company.id,
                "nombre": company.nombre,
                "total_cuentas": company.total_cuentas
            }
            for company in companies_with_stats
        ]
    
    @staticmethod
    def search_companies_advanced(
        db: Session,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Compania]:
        """
        Búsqueda avanzada de compañías
        """
        query = db.query(Compania)
        
        # Búsqueda por texto
        if search_term:
            query = query.filter(
                Compania.nombre.ilike(f"%{search_term}%")
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def validate_company_name(db: Session, nombre: str, exclude_id: Optional[int] = None) -> bool:
        """
        Validar si el nombre de la compañía es único
        """
        query = db.query(Compania).filter(Compania.nombre.ilike(nombre))
        
        if exclude_id:
            query = query.filter(Compania.id != exclude_id)
        
        return query.first() is None
    
    @staticmethod
    def can_delete_company(db: Session, company_id: int) -> tuple[bool, str]:
        """
        Verificar si una compañía puede ser eliminada
        """
        company = db.query(Compania).filter(Compania.id == company_id).first()
        
        if not company:
            return False, "Compañía no encontrada"
        
        # Verificar cuentas bancarias
        if company.cuentas_bancarias:
            return False, f"La compañía tiene {len(company.cuentas_bancarias)} cuenta(s) bancaria(s) asociada(s)"
        
        return True, "La compañía puede ser eliminada"
