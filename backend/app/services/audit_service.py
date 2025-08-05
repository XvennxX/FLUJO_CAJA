from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.auditoria import Auditoria

class AuditService:
    """Servicio para manejo de auditoría del sistema"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def registrar_accion(
        self,
        id_usuario: int,
        accion: str,
        tabla_afectada: Optional[str] = None,
        id_registro_afectado: Optional[int] = None
    ) -> bool:
        """
        Registra una acción en el sistema de auditoría
        
        Args:
            id_usuario: ID del usuario que realiza la acción
            accion: Descripción de la acción realizada
            tabla_afectada: Tabla afectada por la acción
            id_registro_afectado: ID del registro afectado
            
        Returns:
            True si se registró exitosamente, False si no
        """
        try:
            nuevo_registro = Auditoria(
                id_usuario=id_usuario,
                accion=accion,
                fecha=datetime.now()
            )
            
            self.db.add(nuevo_registro)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error al registrar auditoría: {str(e)}")
            return False
    
    def obtener_historial_usuario(
        self,
        id_usuario: int,
        limite: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Obtiene el historial de acciones de un usuario
        
        Args:
            id_usuario: ID del usuario
            limite: Número máximo de registros a devolver
            offset: Número de registros a saltar
            
        Returns:
            Lista de acciones del usuario
        """
        try:
            registros = self.db.query(Auditoria)\
                .filter(Auditoria.id_usuario == id_usuario)\
                .order_by(desc(Auditoria.fecha))\
                .offset(offset)\
                .limit(limite)\
                .all()
            
            return [
                {
                    "id": registro.id_auditoria,
                    "accion": registro.accion,
                    "fecha": registro.fecha,
                    "usuario_id": registro.id_usuario
                }
                for registro in registros
            ]
            
        except Exception as e:
            print(f"Error al obtener historial: {str(e)}")
            return []
    
    def obtener_historial_completo(
        self,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Obtiene el historial completo del sistema
        
        Args:
            fecha_inicio: Fecha de inicio del filtro
            fecha_fin: Fecha de fin del filtro
            limite: Número máximo de registros
            offset: Número de registros a saltar
            
        Returns:
            Lista de todas las acciones del sistema
        """
        try:
            query = self.db.query(Auditoria)
            
            # Aplicar filtros de fecha si se proporcionan
            if fecha_inicio:
                query = query.filter(Auditoria.fecha >= fecha_inicio)
            if fecha_fin:
                query = query.filter(Auditoria.fecha <= fecha_fin)
            
            registros = query\
                .order_by(desc(Auditoria.fecha))\
                .offset(offset)\
                .limit(limite)\
                .all()
            
            return [
                {
                    "id": registro.id_auditoria,
                    "accion": registro.accion,
                    "fecha": registro.fecha,
                    "usuario_id": registro.id_usuario
                }
                for registro in registros
            ]
            
        except Exception as e:
            print(f"Error al obtener historial completo: {str(e)}")
            return []
    
    def contar_acciones_usuario(self, id_usuario: int) -> int:
        """
        Cuenta el total de acciones de un usuario
        
        Args:
            id_usuario: ID del usuario
            
        Returns:
            Número total de acciones
        """
        try:
            return self.db.query(Auditoria)\
                .filter(Auditoria.id_usuario == id_usuario)\
                .count()
        except Exception:
            return 0
