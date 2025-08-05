"""
CRUD para el modelo Auditoria
Operaciones específicas para gestión de auditoría
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.crud.base import CRUDBase
from app.models.auditoria import Auditoria
from app.schemas.auditoria import AuditoriaCreate, AuditoriaUpdate


class CRUDAuditoria(CRUDBase[Auditoria, AuditoriaCreate, AuditoriaUpdate]):
    """CRUD operations para Auditoria"""
    
    def get_by_id(self, db: Session, *, id: int) -> Optional[Auditoria]:
        """Obtener auditoría por ID"""
        return db.query(Auditoria).filter(Auditoria.id_auditoria == id).first()
    
    def get_by_user(self, db: Session, *, user_id: int) -> List[Auditoria]:
        """Obtener registros de auditoría por usuario"""
        return db.query(Auditoria).filter(
            Auditoria.id_usuario == user_id
        ).order_by(desc(Auditoria.fecha_hora)).all()
    
    def get_by_action(self, db: Session, *, action: str) -> List[Auditoria]:
        """Obtener registros por tipo de acción"""
        return db.query(Auditoria).filter(
            Auditoria.accion == action
        ).order_by(desc(Auditoria.fecha_hora)).all()
    
    def get_by_table(self, db: Session, *, table_name: str) -> List[Auditoria]:
        """Obtener registros por tabla afectada"""
        return db.query(Auditoria).filter(
            Auditoria.tabla_afectada == table_name
        ).order_by(desc(Auditoria.fecha_hora)).all()
    
    def get_by_date_range(
        self, 
        db: Session, 
        *, 
        start_date: datetime, 
        end_date: datetime,
        user_id: Optional[int] = None
    ) -> List[Auditoria]:
        """Obtener registros por rango de fechas"""
        query = db.query(Auditoria).filter(
            and_(
                Auditoria.fecha_hora >= start_date,
                Auditoria.fecha_hora <= end_date
            )
        )
        
        if user_id:
            query = query.filter(Auditoria.id_usuario == user_id)
        
        return query.order_by(desc(Auditoria.fecha_hora)).all()
    
    def get_recent_activity(self, db: Session, *, limit: int = 20) -> List[Auditoria]:
        """Obtener actividad reciente"""
        return db.query(Auditoria).order_by(
            desc(Auditoria.fecha_hora)
        ).limit(limit).all()
    
    def get_user_activity_today(self, db: Session, *, user_id: int) -> List[Auditoria]:
        """Obtener actividad del usuario hoy"""
        today = date.today()
        return db.query(Auditoria).filter(
            and_(
                Auditoria.id_usuario == user_id,
                func.date(Auditoria.fecha_hora) == today
            )
        ).order_by(desc(Auditoria.fecha_hora)).all()
    
    def get_action_count_today(self, db: Session) -> Dict[str, int]:
        """Obtener conteo de acciones hoy"""
        today = date.today()
        results = db.query(
            Auditoria.accion,
            func.count(Auditoria.id_auditoria).label('count')
        ).filter(
            func.date(Auditoria.fecha_hora) == today
        ).group_by(Auditoria.accion).all()
        
        return {result.accion: result.count for result in results}
    
    def get_audit_stats(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de auditoría"""
        today = date.today()
        
        # Actividad hoy
        activity_today = db.query(Auditoria).filter(
            func.date(Auditoria.fecha_hora) == today
        ).count()
        
        # Usuarios activos hoy
        active_users_today = db.query(
            func.count(func.distinct(Auditoria.id_usuario))
        ).filter(
            func.date(Auditoria.fecha_hora) == today
        ).scalar()
        
        # Acciones por tipo hoy
        actions_today = self.get_action_count_today(db)
        
        return {
            "actividad_hoy": activity_today,
            "usuarios_activos_hoy": active_users_today,
            "acciones_hoy": actions_today
        }
    
    def log_action(
        self,
        db: Session,
        *,
        user_id: int,
        action: str,
        table_name: str,
        record_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> Auditoria:
        """Registrar una acción de auditoría"""
        audit_record = AuditoriaCreate(
            id_usuario=user_id,
            accion=action,
            tabla_afectada=table_name,
            id_registro=record_id,
            descripcion=description,
            fecha_hora=datetime.now()
        )
        return self.create(db=db, obj_in=audit_record)


# Instancia global del CRUD
auditoria = CRUDAuditoria(Auditoria)
