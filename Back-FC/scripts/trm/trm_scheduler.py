"""
Servicio de automatización para obtener la TRM diariamente
Ejecuta el scraper a las 18:00 (6 PM) todos los días
"""

import schedule
import time
import logging
from datetime import datetime, date
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.trm_scraper import TRMScraper

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trm_scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def job_update_trm():
    """
    Trabajo que actualiza la TRM diaria
    """
    logger.info("=" * 50)
    logger.info("INICIANDO ACTUALIZACIÓN AUTOMÁTICA DE TRM")
    logger.info("=" * 50)
    
    try:
        scraper = TRMScraper()
        
        # Intentar obtener TRM para hoy
        today = date.today()
        success = scraper.update_daily_trm(today)
        
        if success:
            logger.info(f"[OK] TRM actualizada exitosamente para {today}")
        else:
            logger.error(f"[ERROR] Error al actualizar TRM para {today}")
            
            # Intentar obtener TRM del día siguiente (ya que a las 6 PM sale la del día siguiente)
            tomorrow = date.today().replace(day=date.today().day + 1)
            logger.info(f"Intentando obtener TRM para el día siguiente: {tomorrow}")
            
            success_tomorrow = scraper.update_daily_trm(tomorrow)
            if success_tomorrow:
                logger.info(f"[OK] TRM del día siguiente actualizada exitosamente para {tomorrow}")
            else:
                logger.error(f"[ERROR] Error al actualizar TRM del día siguiente para {tomorrow}")
        
    except Exception as e:
        logger.error(f"[ERROR] Error inesperado en la actualización de TRM: {e}")
    
    logger.info("=" * 50)
    logger.info("FINALIZADA ACTUALIZACIÓN AUTOMÁTICA DE TRM")
    logger.info("=" * 50)

def job_test_connection():
    """
    Trabajo de prueba para verificar conectividad
    """
    logger.info("[SYNC] Verificando conectividad...")
    
    try:
        scraper = TRMScraper()
        trm = scraper.get_current_trm()
        
        if trm:
            logger.info(f"[OK] Conexión exitosa. TRM actual: {trm}")
        else:
            logger.warning("[WARNING] No se pudo obtener TRM, pero la conexión funciona")
            
    except Exception as e:
        logger.error(f"[ERROR] Error en verificación de conectividad: {e}")

def main():
    """
    Función principal del scheduler
    """
    logger.info("[INFO] INICIANDO SERVICIO DE AUTOMATIZACIÓN TRM")
    logger.info("[TIME] Programado para ejecutarse diariamente a las 15:15 (3:15 PM)")
    
    # Programar trabajos
    schedule.every().day.at("15:15").do(job_update_trm)
    
    # MODO PRUEBA: Actualizar TRM cada 2 minutos para testing
    schedule.every(2).minutes.do(job_update_trm)
    logger.info("🧪 MODO PRUEBA: También se ejecutará cada 2 minutos para testing")
    
    # Trabajo de prueba cada hora para verificar que el sistema esté funcionando
    schedule.every().hour.do(job_test_connection)
    
    # Ejecutar una vez al iniciar para verificar que todo funciona
    logger.info("[SYNC] Ejecutando verificación inicial...")
    job_test_connection()
    
    # Loop principal
    logger.info("⭐ Servicio iniciado correctamente. Esperando horarios programados...")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
            
        except KeyboardInterrupt:
            logger.info("🛑 Servicio detenido por usuario")
            break
        except Exception as e:
            logger.error(f"[ERROR] Error en el loop principal: {e}")
            time.sleep(300)  # Esperar 5 minutos antes de reintentar

if __name__ == "__main__":
    main()
