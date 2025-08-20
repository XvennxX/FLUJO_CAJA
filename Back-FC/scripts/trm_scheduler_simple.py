"""
Servicio de automatización TRM - Versión simplificada para Windows
"""

import schedule
import time
import logging
from datetime import datetime, date, timedelta
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.trm_scraper import TRMScraper

# Configurar logging sin emojis para Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trm_scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def job_update_trm():
    """
    Trabajo que actualiza la TRM diaria
    A las 7 PM se ejecuta para obtener la TRM del día siguiente
    """
    logger.info("=" * 50)
    logger.info("INICIANDO ACTUALIZACION AUTOMATICA DE TRM")
    logger.info("=" * 50)
    
    try:
        scraper = TRMScraper()
        
        # Obtener fecha actual
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        logger.info(f"Ejecutándose a las 19:00 - Buscando TRM para mañana ({tomorrow})")
        
        # Primero intentar obtener TRM para mañana (disponible a las 6 PM)
        success_tomorrow = scraper.update_daily_trm(tomorrow)
        
        if success_tomorrow:
            logger.info(f"[EXITO] TRM del día siguiente obtenida: {tomorrow}")
        else:
            logger.info(f"TRM para {tomorrow} no disponible aún, obteniendo TRM actual ({today})")
            # Si no está disponible la de mañana, actualizar la de hoy
            success_today = scraper.update_daily_trm(today)
            
            if success_today:
                logger.info(f"[EXITO] TRM actual actualizada: {today}")
            else:
                logger.error(f"[ERROR] No se pudo obtener TRM ni para hoy ni para mañana")
        
    except Exception as e:
        logger.error(f"[ERROR] Error inesperado en la actualizacion de TRM: {e}")
    
    logger.info("=" * 50)
    logger.info("FINALIZADA ACTUALIZACION AUTOMATICA DE TRM")
    logger.info("=" * 50)

def job_test_connection():
    """
    Trabajo de prueba para verificar conectividad
    """
    logger.info("[TEST] Verificando conectividad...")
    
    try:
        scraper = TRMScraper()
        trm = scraper.get_current_trm()
        
        if trm:
            logger.info(f"[EXITO] Conexion exitosa. TRM actual: {trm}")
        else:
            logger.warning("[ADVERTENCIA] No se pudo obtener TRM, pero la conexion funciona")
            
    except Exception as e:
        logger.error(f"[ERROR] Error en verificacion de conectividad: {e}")

def main():
    """
    Función principal del scheduler
    """
    logger.info("INICIANDO SERVICIO DE AUTOMATIZACION TRM - PRODUCCION")
    logger.info("Programado para ejecutarse diariamente a las 19:00 (7:00 PM) - Hora Colombia")
    logger.info("Obtendrá la TRM para el día siguiente según Superintendencia Financiera")
    
    # Programar trabajo diario a las 7 PM
    schedule.every().day.at("19:00").do(job_update_trm)
    
    # Trabajo de prueba cada hora para verificar que el sistema esté funcionando
    schedule.every().hour.do(job_test_connection)
    
    # Ejecutar una vez al iniciar para verificar que todo funciona
    logger.info("Ejecutando verificacion inicial...")
    job_test_connection()
    
    # Loop principal
    logger.info("Servicio iniciado correctamente. Esperando horarios programados...")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
            
        except KeyboardInterrupt:
            logger.info("Servicio detenido por usuario")
            break
        except Exception as e:
            logger.error(f"Error en el loop principal: {e}")
            time.sleep(300)  # Esperar 5 minutos antes de reintentar

if __name__ == "__main__":
    main()
