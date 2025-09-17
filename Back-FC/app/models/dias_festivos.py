"""
Modelo para gestionar días festivos de Colombia.
Permite marcar días como no hábiles para el cálculo de días laborales.
"""
from sqlalchemy import Column, Integer, String, Date, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from app.core.database import Base
from datetime import date
from typing import Optional

class DiaFestivo(Base):
    """
    Modelo para almacenar los días festivos de Colombia.
    
    Campos:
    - id: Identificador único
    - fecha: Fecha del día festivo 
    - nombre: Nombre del festivo (ej: "Día de la Independencia")
    - descripcion: Descripción adicional opcional
    - tipo: Tipo de festivo ('nacional', 'religioso', 'civil')
    - activo: Si el festivo está activo para cálculos
    """
    __tablename__ = "dias_festivos"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, unique=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo = Column(String(50), default='nacional')  # nacional, religioso, civil
    activo = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<DiaFestivo(fecha='{self.fecha}', nombre='{self.nombre}')>"
    
    @classmethod
    def es_festivo(cls, fecha_consulta: date, db) -> bool:
        """
        Verifica si una fecha específica es día festivo.
        
        Args:
            fecha_consulta: Fecha a verificar
            db: Sesión de base de datos
            
        Returns:
            bool: True si es festivo, False si no
        """
        festivo = db.query(cls).filter(
            cls.fecha == fecha_consulta,
            cls.activo == True
        ).first()
        
        return festivo is not None
    
    @classmethod
    def obtener_festivos_rango(cls, fecha_inicio: date, fecha_fin: date, db) -> list:
        """
        Obtiene todos los festivos en un rango de fechas.
        
        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            db: Sesión de base de datos
            
        Returns:
            list: Lista de objetos DiaFestivo
        """
        return db.query(cls).filter(
            cls.fecha >= fecha_inicio,
            cls.fecha <= fecha_fin,
            cls.activo == True
        ).order_by(cls.fecha).all()
    
    def to_dict(self) -> dict:
        """
        Convierte el objeto a diccionario para serialización JSON.
        
        Returns:
            dict: Representación del festivo
        """
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "tipo": self.tipo,
            "activo": self.activo
        }