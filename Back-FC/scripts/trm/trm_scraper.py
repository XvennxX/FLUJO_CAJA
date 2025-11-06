"""
Script para obtener la TRM automáticamente desde la Superintendencia Financiera de Colombia
"""

import requests
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging
from typing import Optional, Dict, Any
import sys
import os
import urllib3
import ssl

# Agregar el directorio padre al path para importar desde app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.trm import TRM

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trm_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TRMScraper:
    def __init__(self):
        # Desactivar advertencias SSL para certificados autofirmados
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # URLs alternativas para obtener la TRM
        self.urls = {
            'datos_abiertos': 'https://www.datos.gov.co/resource/32sa-8pi3.json',  # API de datos abiertos
            'superfinanciera_api': 'https://www.superfinanciera.gov.co/SuperfinancieraWebServiceTRM/TCRMServicesWebService/TCRMServicesWebService?wsdl',
            'banrep_api': 'https://totoro.banrep.gov.co/estadisticas-economicas/rest/consultaDatosService/consultaMercadoCambiario'
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Configurar sesión con manejo de SSL
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        # Permite certificados autofirmados temporalmente
        self.session.verify = False
    
    def get_trm_from_datos_abiertos(self, fecha: date = None) -> Optional[Decimal]:
        """
        Obtiene la TRM desde el portal de datos abiertos del gobierno
        """
        try:
            if fecha is None:
                fecha = date.today()
            
            # Formatear fecha para la API
            fecha_str = fecha.strftime('%Y-%m-%d')
            
            # Construir URL con filtros
            url = f"{self.urls['datos_abiertos']}?vigenciadesde={fecha_str}T00:00:00.000"
            
            logger.info(f"Consultando TRM para fecha {fecha_str} desde datos abiertos...")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                # Los datos vienen ordenados por fecha, tomamos el más reciente
                trm_value = data[0].get('valor', None)
                if trm_value:
                    logger.info(f"TRM obtenida: {trm_value} para fecha {fecha_str}")
                    return Decimal(str(trm_value))
            
            logger.warning(f"No se encontró TRM para la fecha {fecha_str}")
            return None
            
        except requests.RequestException as e:
            logger.error(f"Error de conexión al obtener TRM desde datos abiertos: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener TRM desde datos abiertos: {e}")
            return None
    
    def get_trm_from_banrep(self, fecha: date = None) -> Optional[Decimal]:
        """
        Obtiene la TRM desde la API del Banco de la República
        """
        try:
            if fecha is None:
                fecha = date.today()
            
            # Formato de fecha para Banco de la República
            fecha_str = fecha.strftime('%Y-%m-%d')
            
            # Parámetros para la consulta
            params = {
                'anio': fecha.year,
                'mes': fecha.month,
                'dia': fecha.day
            }
            
            logger.info(f"Consultando TRM para fecha {fecha_str} desde Banco de la República...")
            
            response = self.session.get(
                self.urls['banrep_api'], 
                params=params, 
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extraer valor de TRM de la respuesta
            if 'data' in data and len(data['data']) > 0:
                for item in data['data']:
                    if item.get('fecha') == fecha_str:
                        trm_value = item.get('valor')
                        if trm_value:
                            logger.info(f"TRM obtenida: {trm_value} para fecha {fecha_str}")
                            return Decimal(str(trm_value))
            
            logger.warning(f"No se encontró TRM para la fecha {fecha_str}")
            return None
            
        except requests.RequestException as e:
            logger.error(f"Error de conexión al obtener TRM desde Banco de la República: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener TRM desde Banco de la República: {e}")
            return None
    
    def get_trm_manual_fallback(self) -> Optional[Decimal]:
        """
        Método de respaldo manual para obtener TRM cuando las APIs fallen
        Puedes configurar aquí una TRM manual de emergencia
        """
        logger.warning("Usando valor de TRM manual de respaldo")
        # Aquí puedes poner un valor de emergencia o leer desde un archivo de configuración
        return Decimal("4000.00")  # Valor de ejemplo
    
    def get_current_trm(self, fecha: date = None) -> Optional[Decimal]:
        """
        Intenta obtener la TRM usando múltiples fuentes en orden de preferencia
        """
        if fecha is None:
            fecha = date.today()
        
        # Intentar con datos abiertos primero
        trm = self.get_trm_from_datos_abiertos(fecha)
        if trm:
            return trm
        
        # Intentar con Banco de la República
        trm = self.get_trm_from_banrep(fecha)
        if trm:
            return trm
        
        # Si todo falla, usar respaldo manual (opcional)
        logger.error("No se pudo obtener TRM de ninguna fuente oficial")
        return None
    
    def save_trm_to_database(self, fecha: date, valor: Decimal) -> bool:
        """
        Guarda la TRM en la base de datos
        """
        try:
            db = SessionLocal()
            
            # Verificar si ya existe
            existing_trm = db.query(TRM).filter(TRM.fecha == fecha).first()
            
            if existing_trm:
                # Actualizar valor existente
                existing_trm.valor = valor
                logger.info(f"TRM actualizada para fecha {fecha}: {valor}")
            else:
                # Crear nuevo registro
                new_trm = TRM(fecha=fecha, valor=valor)
                db.add(new_trm)
                logger.info(f"TRM creada para fecha {fecha}: {valor}")
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error al guardar TRM en base de datos: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def update_daily_trm(self, fecha: date = None) -> bool:
        """
        Actualiza la TRM diaria
        """
        if fecha is None:
            fecha = date.today()
        
        logger.info(f"Iniciando actualización de TRM para fecha {fecha}")
        
        # Obtener TRM
        trm_value = self.get_current_trm(fecha)
        
        if trm_value:
            # Guardar en base de datos
            success = self.save_trm_to_database(fecha, trm_value)
            if success:
                logger.info(f"TRM actualizada exitosamente: {fecha} = {trm_value}")
                return True
            else:
                logger.error("Error al guardar TRM en base de datos")
                return False
        else:
            logger.error("No se pudo obtener valor de TRM")
            return False

def main():
    """
    Función principal para ejecutar el scraper
    """
    scraper = TRMScraper()
    
    # Actualizar TRM para hoy
    success = scraper.update_daily_trm()
    
    if success:
        logger.info("Proceso completado exitosamente")
        return 0
    else:
        logger.error("Proceso falló")
        return 1

if __name__ == "__main__":
    exit(main())
