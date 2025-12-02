"""
Servicio para gestión automática de TRM
"""

import logging
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.trm import TRM
from app.models.dias_festivos import DiaFestivo
from typing import Optional

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
            scripts_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scripts')
            if scripts_path not in sys.path:
                sys.path.append(scripts_path)
            
            from trm.trm_scraper import TRMScraper  # type: ignore
            self.scraper = TRMScraper()
            logger.info("✅ TRM Scraper inicializado correctamente")
        except ImportError as e:
            logger.error(f"❌ Error importando TRM Scraper: {e}")
            # Intentar con ruta alternativa
            try:
                from scripts.trm.trm_scraper import TRMScraper
                self.scraper = TRMScraper()
                logger.info("✅ TRM Scraper inicializado correctamente (ruta alternativa)")
            except Exception as e2:
                logger.error(f"❌ Error en ruta alternativa: {e2}")
                self.scraper = None
        except Exception as e:
            logger.error(f"❌ Error inesperado inicializando TRM Scraper: {e}")
            self.scraper = None

    def verificar_trms_faltantes(self, days_back: int = 7) -> dict:
        """
        Verifica y actualiza TRMs faltantes para los últimos N días
        
        Args:
            days_back: Número de días hacia atrás a verificar
            
        Returns:
            dict: Resumen de la operación
        """
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
                    
                    # Intentar crear TRM para la fecha (día hábil: scrapeo; fin de semana/festivo: copiar última disponible)
                    try:
                        if self._upsert_trm_para_fecha(check_date, db):
                            updated_count += 1
                            logger.info(f"✅ TRM registrada para {check_date}")
                        else:
                            error_msg = f"No se pudo registrar TRM para {check_date}"
                            logger.warning(error_msg)
                            errors.append(error_msg)
                    except Exception as e:
                        error_msg = f"Error generando TRM para {check_date}: {e}"
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
        try:
            logger.info(f"🔄 Obteniendo/registrando TRM para fecha específica: {fecha}")
            db = SessionLocal()
            try:
                return self._upsert_trm_para_fecha(fecha, db)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error obteniendo TRM para {fecha}: {e}")
            return False

    # ------------------------
    # Métodos internos helpers
    # ------------------------
    def _es_dia_habil(self, f: date, db: Session) -> bool:
        if f.isoweekday() in (6, 7):  # 6=sábado, 7=domingo
            return False
        try:
            return not DiaFestivo.es_festivo(f, db)
        except Exception:
            # Si falla la consulta de festivos, asumir hábil para intentar scrapeo
            return True

    def _ultima_trm_antes(self, f: date, db: Session) -> Optional[TRM]:
        return db.query(TRM).filter(TRM.fecha < f).order_by(TRM.fecha.desc()).first()

    def _insertar_trm(self, f: date, valor, db: Session) -> bool:
        try:
            existente = db.query(TRM).filter(TRM.fecha == f).first()
            if existente:
                return True
            nuevo = TRM(fecha=f, valor=valor)
            db.add(nuevo)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error insertando TRM para {f}: {e}")
            db.rollback()
            return False

    def _upsert_trm_para_fecha(self, f: date, db: Session) -> bool:
        """Registra TRM para una fecha: si es día hábil intenta scrapeo; si no, copia la última TRM disponible previa.
        Si el scrapeo falla en día hábil, también aplica fallback de copia.
        """
        # Si ya existe, no hacer nada
        if db.query(TRM).filter(TRM.fecha == f).first():
            return True

        # Día hábil: intentar scrapeo
        if self._es_dia_habil(f, db):
            if self.scraper:
                try:
                    if self.scraper.update_daily_trm(f):
                        return True
                except Exception as e:
                    logger.warning(f"Fallo scrapeo TRM para {f}, se intenta fallback por copia: {e}")
            else:
                logger.warning("TRM Scraper no disponible; se intenta fallback por copia")

        # Fines de semana / festivos o fallo de scrapeo: copiar última disponible
        prev_trm = self._ultima_trm_antes(f, db)
        if prev_trm:
            logger.info(f"🛈 Usando TRM previa {prev_trm.fecha}={prev_trm.valor} para completar {f}")
            return self._insertar_trm(f, prev_trm.valor, db)

        logger.error(f"No existe TRM previa para copiar al completar {f}")
        return False

# Instancia global del servicio
trm_service = TRMService()