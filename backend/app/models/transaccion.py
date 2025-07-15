"""
Modelo Transaccion - Movimientos diarios de ingresos y egresos
"""

from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, Boolean, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from decimal import Decimal
from datetime import date
from app.core.database import Base


class Transaccion(Base):
    """
    Modelo de Transacción - Representa cada movimiento de dinero
    
    Equivale a cada celda en las hojas Excel donde se registran montos por día y categoría
    """
    __tablename__ = "transacciones"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, index=True)
    monto = Column(Numeric(15, 2), nullable=False)  # Precisión de 15 dígitos, 2 decimales
    descripcion = Column(Text, nullable=True)
    
    # Referencias
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Campos adicionales para auditoría y control
    numero_comprobante = Column(String(50), nullable=True)  # Número de factura, recibo, etc.
    area_origen = Column(String(50), nullable=True)  # "Tesorería", "Pagaduría", "Mesa de Dinero"
    
    # Estado y validación
    esta_confirmada = Column(Boolean, default=False)  # Para validaciones de supervisión
    requiere_aprobacion = Column(Boolean, default=False)
    aprobada_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_aprobacion = Column(DateTime(timezone=True), nullable=True)
    
    # Metadatos
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="transacciones")
    usuario = relationship("Usuario", back_populates="transacciones", foreign_keys=[usuario_id])
    usuario_aprobador = relationship("Usuario", foreign_keys=[aprobada_por])
    
    def __repr__(self):
        return f"<Transaccion(id={self.id}, fecha={self.fecha}, monto={self.monto}, categoria='{self.categoria.nombre if self.categoria else 'N/A'}')>"
    
    @property
    def es_ingreso(self) -> bool:
        """Verifica si la transacción es un ingreso"""
        return self.categoria and self.categoria.es_ingreso
    
    @property
    def es_egreso(self) -> bool:
        """Verifica si la transacción es un egreso"""
        return self.categoria and self.categoria.es_egreso
    
    @property
    def monto_formato(self) -> str:
        """Retorna el monto formateado como moneda colombiana"""
        return f"${self.monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @property
    def flujo_neto(self) -> Decimal:
        """
        Retorna el impacto neto en el flujo de caja
        Ingresos suman (+), egresos restan (-)
        """
        if self.es_ingreso:
            return self.monto
        else:
            return -self.monto
    
    def puede_ser_editada_por(self, usuario) -> bool:
        """
        Verifica si un usuario puede editar esta transacción
        """
        # El usuario que la creó siempre puede editarla (si no está confirmada)
        if self.usuario_id == usuario.id and not self.esta_confirmada:
            return True
        
        # Tesorería puede editar todo
        if usuario.es_tesoreria:
            return True
        
        # Pagaduría solo puede editar egresos
        if usuario.es_pagaduria and self.es_egreso:
            return True
        
        # Mesa de dinero no puede editar nada
        return False
    
    def puede_ser_eliminada_por(self, usuario) -> bool:
        """
        Verifica si un usuario puede eliminar esta transacción
        """
        # Solo tesorería puede eliminar transacciones confirmadas
        if self.esta_confirmada and not usuario.es_tesoreria:
            return False
        
        return self.puede_ser_editada_por(usuario)
    
    def confirmar(self, usuario):
        """Confirma la transacción"""
        if usuario.es_tesoreria:
            self.esta_confirmada = True
            self.aprobada_por = usuario.id
            self.fecha_aprobacion = func.now()
    
    @classmethod
    def calcular_saldo_dia(cls, fecha: date, session) -> Decimal:
        """
        Calcula el saldo neto del día (ingresos - egresos)
        """
        from sqlalchemy import func, and_
        from app.models.categoria import TipoCategoria
        
        # Sumar ingresos del día
        ingresos = session.query(func.coalesce(func.sum(cls.monto), 0))\
            .join(cls.categoria)\
            .filter(and_(
                cls.fecha == fecha,
                cls.categoria.tipo == TipoCategoria.INGRESO
            )).scalar()
        
        # Sumar egresos del día  
        egresos = session.query(func.coalesce(func.sum(cls.monto), 0))\
            .join(cls.categoria)\
            .filter(and_(
                cls.fecha == fecha,
                cls.categoria.tipo == TipoCategoria.EGRESO
            )).scalar()
        
        return Decimal(str(ingresos)) - Decimal(str(egresos))
    
    @classmethod
    def calcular_flujo_acumulado(cls, fecha_hasta: date, session) -> Decimal:
        """
        Calcula el flujo acumulado hasta una fecha específica
        """
        from sqlalchemy import func, and_
        from app.models.categoria import TipoCategoria
        
        # Sumar todos los ingresos hasta la fecha
        ingresos_totales = session.query(func.coalesce(func.sum(cls.monto), 0))\
            .join(cls.categoria)\
            .filter(and_(
                cls.fecha <= fecha_hasta,
                cls.categoria.tipo == TipoCategoria.INGRESO
            )).scalar()
        
        # Sumar todos los egresos hasta la fecha
        egresos_totales = session.query(func.coalesce(func.sum(cls.monto), 0))\
            .join(cls.categoria)\
            .filter(and_(
                cls.fecha <= fecha_hasta,
                cls.categoria.tipo == TipoCategoria.EGRESO
            )).scalar()
        
        return Decimal(str(ingresos_totales)) - Decimal(str(egresos_totales))
