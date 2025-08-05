"""
CRUD para el modelo Usuario
Operaciones específicas para gestión de usuarios
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.crud.base import CRUDBase
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import get_password_hash


class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    """CRUD operations para Usuario"""
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[Usuario]:
        """Obtener usuario por email"""
        return db.query(Usuario).filter(Usuario.correo == email).first()
    
    def get_by_id(self, db: Session, *, id: int) -> Optional[Usuario]:
        """Obtener usuario por ID"""
        return db.query(Usuario).filter(Usuario.id_usuario == id).first()
    
    def create(self, db: Session, *, obj_in: UsuarioCreate) -> Usuario:
        """Crear nuevo usuario con contraseña hasheada"""
        create_data = obj_in.dict()
        create_data.pop("contraseña")
        
        db_obj = Usuario(
            **create_data,
            contraseña=get_password_hash(obj_in.contraseña),
            estado=True
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, 
        db: Session, 
        *, 
        db_obj: Usuario, 
        obj_in: UsuarioUpdate
    ) -> Usuario:
        """Actualizar usuario (hashea contraseña si se proporciona)"""
        update_data = obj_in.dict(exclude_unset=True)
        
        if "contraseña" in update_data:
            update_data["contraseña"] = get_password_hash(update_data["contraseña"])
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Obtener usuarios activos"""
        return db.query(Usuario).filter(
            Usuario.estado == True
        ).offset(skip).limit(limit).all()
    
    def get_by_role(self, db: Session, *, role_id: int) -> List[Usuario]:
        """Obtener usuarios por rol"""
        return db.query(Usuario).filter(Usuario.id_rol == role_id).all()
    
    def search_users(
        self, 
        db: Session, 
        *, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Usuario]:
        """Buscar usuarios por nombre o email"""
        return db.query(Usuario).filter(
            or_(
                Usuario.nombre_completo.ilike(f"%{search_term}%"),
                Usuario.correo.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit).all()
    
    def activate_user(self, db: Session, *, user_id: int) -> Optional[Usuario]:
        """Activar usuario"""
        user = self.get_by_id(db, id=user_id)
        if user:
            user.estado = True
            db.commit()
            db.refresh(user)
        return user
    
    def deactivate_user(self, db: Session, *, user_id: int) -> Optional[Usuario]:
        """Desactivar usuario"""
        user = self.get_by_id(db, id=user_id)
        if user:
            user.estado = False
            db.commit()
            db.refresh(user)
        return user
    
    def is_active(self, user: Usuario) -> bool:
        """Verificar si el usuario está activo"""
        return user.estado
    
    def get_users_stats(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de usuarios"""
        total_users = db.query(Usuario).count()
        active_users = db.query(Usuario).filter(Usuario.estado == True).count()
        inactive_users = total_users - active_users
        
        return {
            "total": total_users,
            "activos": active_users,
            "inactivos": inactive_users
        }


# Instancia global del CRUD
usuario = CRUDUsuario(Usuario)
