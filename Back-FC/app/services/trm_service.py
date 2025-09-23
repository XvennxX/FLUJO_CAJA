"""
Servicio para gestión automática de TRM
"""

import logging
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.trm import TRM

logger = logging.getLogger(__name__)

class TRMService:
    def __init__(self):
        self.scraper = None
        self._init_scraper()

    def _init_scraper(self):
        """Inicializar el scraper de TRM"""
        try:
            import sys
            import os
            # Agregar scripts al path si no existe
            scripts_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
            if scripts_path not in sys.path:
                sys.path.append(scripts_path)
            
            from trm.trm_scraper import TRMScraper
            self.scraper = TRMScraper()
            logger.info("TRM Scraper inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando TRM Scraper: {e}")
            self.scraper = None

    def verificar_trms_faltantes(self, days_back: int = 7) -> dict:
        """
        Verifica y actualiza TRMs faltantes para los últimos N días
        
        Args:
            days_back: Número de días hacia atrás a verificar
            
        Returns:
            dict: Resumen de la operación
        """
        if not self.scraper:
            logger.warning("TRM Scraper no disponible")
            return {
                "success": False,
                "error": "TRM Scraper no disponible",
                "missing_count": 0,
                "updated_count": 0
            }

        logger.info(f"🔍 Verificando TRMs faltantes para los últimos {days_back} días")
        
        today = date.today()
        missing_count = 0
        updated_count = 0
        errors = []
        
        db = SessionLocal()
        try:
            for i in range(days_back, 0, -1):
                check_date = today - timedelta(days=i)
                
                # Verificar si existe TRM para esta fecha
                existing_trm = db.query(TRM).filter(TRM.fecha == check_date).first()
                
                if not existing_trm:
                    logger.info(f"❌ TRM faltante para {check_date}")
                    missing_count += 1
                    
                    # Intentar actualizar
                    try:
                        success = self.scraper.update_daily_trm(check_date)
                        
                        if success:
                            logger.info(f"✅ TRM actualizada exitosamente para {check_date}")
                            updated_count += 1
                        else:
                            error_msg = f"No se pudo obtener TRM para {check_date} (posible día no hábil)"
                            logger.warning(error_msg)
                            errors.append(error_msg)
                            
                    except Exception as e:
                        error_msg = f"Error actualizando TRM para {check_date}: {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                else:
                    logger.debug(f"✅ TRM ya existe para {check_date}: ${existing_trm.valor:,.2f}")
                    
        finally:
            db.close()
        
        result = {
            "success": True,
            "missing_count": missing_count,
            "updated_count": updated_count,
            "failed_count": missing_count - updated_count,
            "errors": errors
        }
        
        logger.info(f"📊 Resumen TRM: {missing_count} faltantes, {updated_count} actualizadas")
        return result

    def obtener_trm_fecha(self, fecha: date) -> bool:
        """
        Obtiene TRM para una fecha específica
        
        Args:
            fecha: Fecha para la cual obtener la TRM
            
        Returns:
            bool: True si se obtuvo exitosamente
        """
        if not self.scraper:
            logger.warning("TRM Scraper no disponible")
            return False

        try:
            logger.info(f"🔄 Obteniendo TRM para fecha específica: {fecha}")
            success = self.scraper.update_daily_trm(fecha)
            
            if success:
                logger.info(f"✅ TRM obtenida exitosamente para {fecha}")
            else:
                logger.warning(f"❌ No se pudo obtener TRM para {fecha}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error obteniendo TRM para {fecha}: {e}")
            return False

# Instancia global del servicio
trm_service = TRMService()