"""
Clase base para operaciones CRUD
Implementa el patrón Repository para acceso a datos
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Clase base para operaciones CRUD
    Implementa operaciones estándar de Create, Read, Update, Delete
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Objeto CRUD con métodos por defecto para Create, Read, Update, Delete
        
        **Parámetros**
        * `model`: Clase del modelo SQLAlchemy
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Obtener un registro por ID"""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError:
            return None

    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Obtener múltiples registros con paginación y filtros"""
        try:
            query = db.query(self.model)
            
            # Aplicar filtros si se proporcionan
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        query = query.filter(getattr(self.model, key) == value)
            
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError:
            return []

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Crear un nuevo registro"""
        try:
            obj_in_data = obj_in.dict()
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError:
            db.rollback()
            raise

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Actualizar un registro existente"""
        try:
            obj_data = db_obj.__dict__
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError:
            db.rollback()
            raise

    def remove(self, db: Session, *, id: int) -> ModelType:
        """Eliminar un registro por ID"""
        try:
            obj = db.query(self.model).get(id)
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except SQLAlchemyError:
            db.rollback()
            raise

    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar registros con filtros opcionales"""
        try:
            query = db.query(self.model)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        query = query.filter(getattr(self.model, key) == value)
            
            return query.count()
        except SQLAlchemyError:
            return 0

    def exists(self, db: Session, id: Any) -> bool:
        """Verificar si existe un registro por ID"""
        try:
            return db.query(self.model).filter(self.model.id == id).first() is not None
        except SQLAlchemyError:
            return False

    def soft_delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        """Eliminación lógica (cambiar estado a inactivo)"""
        try:
            obj = db.query(self.model).get(id)
            if obj and hasattr(obj, 'estado'):
                obj.estado = False
                db.add(obj)
                db.commit()
                db.refresh(obj)
            return obj
        except SQLAlchemyError:
            db.rollback()
            raise
