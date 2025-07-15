"""
Modelo Categoria - Clasificación de ingresos y egresos
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class TipoCategoria(str, enum.Enum):
    """Enum para el tipo de categoría"""
    INGRESO = "ingreso"
    EGRESO = "egreso"


class Categoria(Base):
    """
    Modelo de Categoría para clasificar transacciones
    
    Ejemplos de categorías:
    - INGRESOS: Ventas, Servicios, Intereses, Otros ingresos
    - EGRESOS: Nómina, Proveedores, Servicios públicos, Impuestos, etc.
    """
    __tablename__ = "categorias"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    tipo = Column(Enum(TipoCategoria), nullable=False)
    
    # Configuración y estado
    esta_activa = Column(Boolean, default=True)
    es_categoria_sistema = Column(Boolean, default=False)  # No se puede eliminar
    orden = Column(Integer, default=0)  # Para ordenar en la UI
    
    # Código contable (opcional)
    codigo_contable = Column(String(20), nullable=True, unique=True)
    
    # Color para la UI (hex)
    color = Column(String(7), default="#6B7280")  # gray-500
    
    # Metadatos
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    creado_por = Column(Integer, nullable=True)
    
    # Relaciones
    transacciones = relationship("Transaccion", back_populates="categoria", lazy="dynamic")
    
    def __repr__(self):
        return f"<Categoria(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo.value}')>"
    
    @property
    def es_ingreso(self) -> bool:
        """Verifica si la categoría es de tipo ingreso"""
        return self.tipo == TipoCategoria.INGRESO
    
    @property
    def es_egreso(self) -> bool:
        """Verifica si la categoría es de tipo egreso"""
        return self.tipo == TipoCategoria.EGRESO
    
    @property
    def total_transacciones(self) -> int:
        """Retorna el número total de transacciones de esta categoría"""
        return self.transacciones.count()
    
    def puede_ser_eliminada(self) -> bool:
        """
        Verifica si la categoría puede ser eliminada
        No se pueden eliminar categorías del sistema o con transacciones asociadas
        """
        return not self.es_categoria_sistema and self.total_transacciones == 0


# Datos por defecto de categorías del sistema
CATEGORIAS_SISTEMA = [
    # INGRESOS
    {"nombre": "Ventas", "tipo": TipoCategoria.INGRESO, "codigo_contable": "4100", "color": "#10B981"},
    {"nombre": "Servicios", "tipo": TipoCategoria.INGRESO, "codigo_contable": "4200", "color": "#059669"},
    {"nombre": "Intereses Bancarios", "tipo": TipoCategoria.INGRESO, "codigo_contable": "4300", "color": "#047857"},
    {"nombre": "Otros Ingresos", "tipo": TipoCategoria.INGRESO, "codigo_contable": "4900", "color": "#065F46"},
    
    # EGRESOS
    {"nombre": "Nómina", "tipo": TipoCategoria.EGRESO, "codigo_contable": "5100", "color": "#EF4444"},
    {"nombre": "Proveedores", "tipo": TipoCategoria.EGRESO, "codigo_contable": "5200", "color": "#DC2626"},
    {"nombre": "Servicios Públicos", "tipo": TipoCategoria.EGRESO, "codigo_contable": "5300", "color": "#B91C1C"},
    {"nombre": "Arriendo", "tipo": TipoCategoria.EGRESO, "codigo_contable": "5400", "color": "#991B1B"},
    {"nombre": "Impuestos", "tipo": TipoCategoria.EGRESO, "codigo_contable": "5500", "color": "#7F1D1D"},
    {"nombre": "Gastos Administrativos", "tipo": TipoCategoria.EGRESO, "codigo_contable": "5600", "color": "#F59E0B"},
    {"nombre": "Gastos Operacionales", "tipo": TipoCategoria.EGRESO, "codigo_contable": "5700", "color": "#D97706"},
    {"nombre": "Otros Egresos", "tipo": TipoCategoria.EGRESO, "codigo_contable": "5900", "color": "#92400E"},
]
