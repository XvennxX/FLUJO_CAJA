"""
CRUD para el modelo Rol
Operaciones específicas para gestión de roles
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.rol import Rol
from app.schemas.rol import RolBase


class CRUDRol(CRUDBase[Rol, RolBase, RolBase]):
    """CRUD operations para Rol"""
    
    def get_by_id(self, db: Session, *, id: int) -> Optional[Rol]:
        """Obtener rol por ID"""
        return db.query(Rol).filter(Rol.id_rol == id).first()
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Rol]:
        """Obtener rol por nombre"""
        return db.query(Rol).filter(Rol.nombre_rol == name).first()
    
    def get_all(self, db: Session) -> List[Rol]:
        """Obtener todos los roles"""
        return db.query(Rol).all()
    
    def create_role(self, db: Session, *, nombre: str) -> Rol:
        """Crear nuevo rol"""
        db_obj = Rol(nombre_rol=nombre)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Instancia global del CRUD
rol = CRUDRol(Rol)
