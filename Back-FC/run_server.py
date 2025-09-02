#!/usr/bin/env python3
"""
Script para iniciar el servidor de desarrollo con verificación automática de TRM
"""

import uvicorn
import sys
import os
from datetime import date, timedelta
import logging

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verificar_trm_startup():
    """Verifica TRMs faltantes al iniciar el servidor"""
    try:
        logger.info("🔍 Verificando TRMs faltantes al iniciar...")
        
        from scripts.trm.trm_scraper import TRMScraper
        from app.core.database import SessionLocal
        from app.models.trm import TRM
        
        scraper = TRMScraper()
        today = date.today()
        
        # Verificar últimos 3 días y hoy
        for i in range(3, -1, -1):  # 3 días atrás hasta hoy
            check_date = today - timedelta(days=i)
            
            db = SessionLocal()
            try:
                existing_trm = db.query(TRM).filter(TRM.fecha == check_date).first()
                
                if not existing_trm:
                    logger.info(f"❌ TRM faltante para {check_date}, actualizando...")
                    success = scraper.update_daily_trm(check_date)
                    if success:
                        logger.info(f"✅ TRM actualizada para {check_date}")
                    else:
                        logger.warning(f"⚠️ No se pudo actualizar TRM para {check_date}")
                else:
                    logger.info(f"✅ TRM existe para {check_date}: ${existing_trm.valor:,.2f}")
                        
            except Exception as e:
                logger.error(f"❌ Error verificando TRM para {check_date}: {e}")
            finally:
                db.close()
        
        logger.info("🚀 Verificación de TRM completada")
        
    except Exception as e:
        logger.error(f"❌ Error en verificación de TRM: {e}")
        logger.info("⚠️ El servidor continuará sin verificación de TRM")

if __name__ == "__main__":
    print("🚀 Iniciando servidor FastAPI...")
    print("📊 Dashboard disponible en: http://localhost:8000/docs")
    print("🔗 API Base URL: http://localhost:8000/api/v1")
    print("⏹️  Presiona Ctrl+C para detener el servidor")
    print()
    
    # Verificar TRMs antes de iniciar el servidor
    verificar_trm_startup()
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
