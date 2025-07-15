"""
Modelo MesFlujo - Control mensual equivalente a las hojas Excel por mes
"""

from sqlalchemy import Column, Integer, DateTime, Numeric, Boolean, String, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from decimal import Decimal
from datetime import date, datetime
from app.core.database import Base


class MesFlujo(Base):
    """
    Modelo de control mensual de flujo de caja
    
    Equivale a cada hoja Excel (MAYO2025.xlsx, JUNIO2025.xlsx, etc.)
    Mantiene el control de saldos iniciales, finales y estado del período
    """
    __tablename__ = "meses_flujo"
    
    id = Column(Integer, primary_key=True, index=True)
    mes = Column(Integer, nullable=False)  # 1-12
    anio = Column(Integer, nullable=False)
    
    # Saldos
    saldo_inicial = Column(Numeric(15, 2), nullable=False, default=0)
    saldo_final = Column(Numeric(15, 2), nullable=True)  # Se calcula al cerrar
    
    # Estado del período
    esta_cerrado = Column(Boolean, default=False)
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)
    cerrado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    # Metadatos de control
    total_ingresos = Column(Numeric(15, 2), default=0)
    total_egresos = Column(Numeric(15, 2), default=0)
    flujo_neto = Column(Numeric(15, 2), default=0)
    
    # Información adicional
    observaciones = Column(String(500), nullable=True)
    archivo_excel_original = Column(String(255), nullable=True)  # Referencia al Excel original
    
    # Metadatos
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    usuario_cierre = relationship("Usuario", foreign_keys=[cerrado_por])
    
    def __repr__(self):
        return f"<MesFlujo(id={self.id}, mes={self.mes}, anio={self.anio}, cerrado={self.esta_cerrado})>"
    
    @property
    def nombre_mes(self) -> str:
        """Retorna el nombre del mes en español"""
        nombres_meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        return nombres_meses.get(self.mes, f"Mes {self.mes}")
    
    @property
    def periodo_completo(self) -> str:
        """Retorna el período completo como string"""
        return f"{self.nombre_mes} {self.anio}"
    
    @property
    def fecha_inicio(self) -> date:
        """Retorna la fecha de inicio del mes"""
        return date(self.anio, self.mes, 1)
    
    @property
    def fecha_fin(self) -> date:
        """Retorna la fecha de fin del mes"""
        import calendar
        ultimo_dia = calendar.monthrange(self.anio, self.mes)[1]
        return date(self.anio, self.mes, ultimo_dia)
    
    @property
    def dias_mes(self) -> int:
        """Retorna el número de días del mes"""
        import calendar
        return calendar.monthrange(self.anio, self.mes)[1]
    
    def puede_ser_cerrado(self) -> bool:
        """Verifica si el mes puede ser cerrado"""
        # No se puede cerrar si ya está cerrado
        if self.esta_cerrado:
            return False
        
        # No se puede cerrar un mes futuro
        hoy = date.today()
        if self.fecha_fin > hoy:
            return False
            
        return True
    
    def calcular_totales(self, session):
        """Calcula y actualiza los totales del mes"""
        from app.models.transaccion import Transaccion
        from app.models.categoria import TipoCategoria
        from sqlalchemy import func, and_
        
        # Calcular total de ingresos
        self.total_ingresos = session.query(func.coalesce(func.sum(Transaccion.monto), 0))\
            .join(Transaccion.categoria)\
            .filter(and_(
                func.extract('month', Transaccion.fecha) == self.mes,
                func.extract('year', Transaccion.fecha) == self.anio,
                Transaccion.categoria.tipo == TipoCategoria.INGRESO
            )).scalar()
        
        # Calcular total de egresos
        self.total_egresos = session.query(func.coalesce(func.sum(Transaccion.monto), 0))\
            .join(Transaccion.categoria)\
            .filter(and_(
                func.extract('month', Transaccion.fecha) == self.mes,
                func.extract('year', Transaccion.fecha) == self.anio,
                Transaccion.categoria.tipo == TipoCategoria.EGRESO
            )).scalar()
        
        # Calcular flujo neto
        self.flujo_neto = self.total_ingresos - self.total_egresos
        
        # Calcular saldo final
        self.saldo_final = self.saldo_inicial + self.flujo_neto
    
    def cerrar_mes(self, usuario, session):
        """
        Cierra el mes y establece el saldo inicial del siguiente
        """
        if not self.puede_ser_cerrado():
            raise ValueError("No se puede cerrar este mes")
        
        # Calcular totales finales
        self.calcular_totales(session)
        
        # Marcar como cerrado
        self.esta_cerrado = True
        self.fecha_cierre = datetime.now()
        self.cerrado_por = usuario.id
        
        # Crear o actualizar el mes siguiente
        mes_siguiente = self.mes + 1 if self.mes < 12 else 1
        anio_siguiente = self.anio if self.mes < 12 else self.anio + 1
        
        # Buscar o crear el mes siguiente
        proximo_mes = session.query(MesFlujo).filter(
            MesFlujo.mes == mes_siguiente,
            MesFlujo.anio == anio_siguiente
        ).first()
        
        if not proximo_mes:
            proximo_mes = MesFlujo(
                mes=mes_siguiente,
                anio=anio_siguiente,
                saldo_inicial=self.saldo_final
            )
            session.add(proximo_mes)
        else:
            # Actualizar saldo inicial si no está cerrado
            if not proximo_mes.esta_cerrado:
                proximo_mes.saldo_inicial = self.saldo_final
    
    @classmethod
    def obtener_o_crear_mes_actual(cls, session):
        """Obtiene o crea el registro del mes actual"""
        hoy = date.today()
        
        mes_actual = session.query(cls).filter(
            cls.mes == hoy.month,
            cls.anio == hoy.year
        ).first()
        
        if not mes_actual:
            # Buscar el mes anterior para obtener saldo inicial
            mes_anterior = hoy.month - 1 if hoy.month > 1 else 12
            anio_anterior = hoy.year if hoy.month > 1 else hoy.year - 1
            
            mes_previo = session.query(cls).filter(
                cls.mes == mes_anterior,
                cls.anio == anio_anterior
            ).first()
            
            saldo_inicial = mes_previo.saldo_final if mes_previo and mes_previo.saldo_final else Decimal('0')
            
            mes_actual = cls(
                mes=hoy.month,
                anio=hoy.year,
                saldo_inicial=saldo_inicial
            )
            session.add(mes_actual)
            session.commit()
        
        return mes_actual
