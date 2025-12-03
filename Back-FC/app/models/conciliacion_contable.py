"""
Modelo para la conciliación contable diaria
"""
from sqlalchemy import Column, Integer, String, Date, DECIMAL, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from decimal import Decimal

class ConciliacionContable(Base):
    """
    Modelo para manejar las conciliaciones contables diarias por empresa
    """
    __tablename__ = "conciliaciones_contables"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("companias.id"), nullable=False)
    
    # Totales calculados automáticamente desde transacciones
    total_pagaduria = Column(DECIMAL(15, 2), nullable=False, default=0)
    total_tesoreria = Column(DECIMAL(15, 2), nullable=False, default=0)
    
    # Total manual ingresado por el usuario
    total_centralizadora = Column(DECIMAL(15, 2), nullable=True)
    
    # Diferencia calculada: (total_pagaduria + total_tesoreria) - total_centralizadora
    diferencia = Column(DECIMAL(15, 2), nullable=True)
    
    # Estado de la conciliación
    estado = Column(String(20), nullable=False, default="Pendiente")  # Pendiente, Evaluado, Confirmado
    
    # Observaciones adicionales
    observaciones = Column(Text, nullable=True)
    
    # Timestamps
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relación con empresa
    empresa = relationship("Compania", back_populates="conciliaciones")
    
    @property
    def total_calculado(self):
        """Total calculado: suma de pagaduría + tesorería"""
        return (self.total_pagaduria or 0) + (self.total_tesoreria or 0)
    
    @property
    def diferencia_calculada(self):
        """Calcula la diferencia entre total calculado y centralizadora"""
        if self.total_centralizadora is None:
            return None
        return self.total_calculado - self.total_centralizadora
    
    @property
    def estado_conciliacion(self):
        """Determina el estado basado en la diferencia"""
        if self.total_centralizadora is None:
            return "Pendiente"
        
        diferencia = abs(self.diferencia_calculada or 0)
        
        if diferencia == 0:
            return "Cuadrado"
        elif diferencia <= 100:  # Tolerancia de $100
            return "Con Diferencia Menor"
        else:
            return "Con Diferencia"
    
    def __repr__(self):
        return f"<ConciliacionContable(fecha={self.fecha}, empresa_id={self.empresa_id}, estado={self.estado})>"