"""
Servicio para gestionar días hábiles (lunes a viernes, excluyendo festivos).
Este servicio determina qué días son laborables en Colombia.
"""
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.dias_festivos import DiaFestivo


class DiasHabilesService:
    """
    Servicio para determinar días hábiles en Colombia.
    
    Un día hábil es:
    - Lunes a viernes (weekday 0-4)
    - No es día festivo según la base de datos
    """
    
    def __init__(self, db: Session):
        """
        Inicializar servicio con sesión de base de datos.
        
        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
    
    def es_dia_habil(self, fecha: date) -> bool:
        """
        Determinar si una fecha es día hábil.
        
        Args:
            fecha: Fecha a evaluar
            
        Returns:
            True si es día hábil, False si es fin de semana o festivo
        """
        # Verificar si es fin de semana (sábado = 5, domingo = 6)
        if fecha.weekday() >= 5:
            return False
        
        # Verificar si es día festivo
        if DiaFestivo.es_festivo(fecha, self.db):
            return False
        
        return True
    
    def proximo_dia_habil(self, fecha: date, incluir_fecha_actual: bool = False) -> date:
        """
        Encontrar el próximo día hábil a partir de una fecha.
        
        Args:
            fecha: Fecha de referencia
            incluir_fecha_actual: Si True, puede retornar la misma fecha si es hábil
            
        Returns:
            Fecha del próximo día hábil
        """
        if incluir_fecha_actual and self.es_dia_habil(fecha):
            return fecha
        
        fecha_actual = fecha + timedelta(days=1)
        
        # Buscar hasta encontrar un día hábil (máximo 14 días para evitar loops)
        contador = 0
        while not self.es_dia_habil(fecha_actual) and contador < 14:
            fecha_actual += timedelta(days=1)
            contador += 1
        
        return fecha_actual
    
    def anterior_dia_habil(self, fecha: date, incluir_fecha_actual: bool = False) -> date:
        """
        Encontrar el día hábil anterior a partir de una fecha.
        
        Args:
            fecha: Fecha de referencia
            incluir_fecha_actual: Si True, puede retornar la misma fecha si es hábil
            
        Returns:
            Fecha del día hábil anterior
        """
        if incluir_fecha_actual and self.es_dia_habil(fecha):
            return fecha
        
        fecha_actual = fecha - timedelta(days=1)
        
        # Buscar hasta encontrar un día hábil (máximo 14 días para evitar loops)
        contador = 0
        while not self.es_dia_habil(fecha_actual) and contador < 14:
            fecha_actual -= timedelta(days=1)
            contador += 1
        
        return fecha_actual
    
    def obtener_dias_habiles_rango(
        self, 
        fecha_inicio: date, 
        fecha_fin: date
    ) -> List[date]:
        """
        Obtener lista de días hábiles en un rango de fechas.
        
        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            
        Returns:
            Lista de fechas que son días hábiles
        """
        dias_habiles = []
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            if self.es_dia_habil(fecha_actual):
                dias_habiles.append(fecha_actual)
            fecha_actual += timedelta(days=1)
        
        return dias_habiles
    
    def contar_dias_habiles_rango(
        self, 
        fecha_inicio: date, 
        fecha_fin: date
    ) -> int:
        """
        Contar días hábiles en un rango de fechas.
        
        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            
        Returns:
            Número de días hábiles en el rango
        """
        return len(self.obtener_dias_habiles_rango(fecha_inicio, fecha_fin))
    
    def obtener_ultimo_dia_habil_mes(self, año: int, mes: int) -> date:
        """
        Obtener el último día hábil de un mes específico.
        
        Args:
            año: Año del mes
            mes: Mes (1-12)
            
        Returns:
            Fecha del último día hábil del mes
        """
        # Obtener último día del mes
        if mes == 12:
            ultimo_dia = date(año + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia = date(año, mes + 1, 1) - timedelta(days=1)
        
        return self.anterior_dia_habil(ultimo_dia, incluir_fecha_actual=True)
    
    def obtener_primer_dia_habil_mes(self, año: int, mes: int) -> date:
        """
        Obtener el primer día hábil de un mes específico.
        
        Args:
            año: Año del mes
            mes: Mes (1-12)
            
        Returns:
            Fecha del primer día hábil del mes
        """
        primer_dia = date(año, mes, 1)
        return self.proximo_dia_habil(primer_dia, incluir_fecha_actual=True)
    
    def es_ultimo_dia_habil_mes(self, fecha: date) -> bool:
        """
        Determinar si una fecha es el último día hábil del mes.
        
        Args:
            fecha: Fecha a evaluar
            
        Returns:
            True si es el último día hábil del mes
        """
        if not self.es_dia_habil(fecha):
            return False
        
        ultimo_dia_habil = self.obtener_ultimo_dia_habil_mes(fecha.year, fecha.month)
        return fecha == ultimo_dia_habil
    
    def obtener_proximo_dia_habil_desde_hoy(self) -> date:
        """
        Obtener el próximo día hábil desde hoy.
        
        Returns:
            Fecha del próximo día hábil (puede ser hoy si es hábil)
        """
        hoy = date.today()
        return self.proximo_dia_habil(hoy, incluir_fecha_actual=True)
    
    def obtener_info_dia(self, fecha: date) -> dict:
        """
        Obtener información completa sobre un día específico.
        
        Args:
            fecha: Fecha a analizar
            
        Returns:
            Diccionario con información del día
        """
        es_habil = self.es_dia_habil(fecha)
        es_fin_semana = fecha.weekday() >= 5
        es_festivo = DiaFestivo.es_festivo(fecha, self.db)
        
        # Obtener información del festivo si aplica
        festivo_info = None
        if es_festivo:
            festivo = self.db.query(DiaFestivo).filter(
                DiaFestivo.fecha == fecha,
                DiaFestivo.activo == True
            ).first()
            if festivo:
                festivo_info = festivo.to_dict()
        
        return {
            "fecha": fecha.isoformat(),
            "es_habil": es_habil,
            "es_fin_semana": es_fin_semana,
            "es_festivo": es_festivo,
            "festivo": festivo_info,
            "dia_semana": fecha.strftime("%A"),
            "proximo_habil": self.proximo_dia_habil(fecha).isoformat(),
            "anterior_habil": self.anterior_dia_habil(fecha).isoformat()
        }