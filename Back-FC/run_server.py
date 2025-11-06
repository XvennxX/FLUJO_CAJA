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
        logger.info("=" * 60)
        logger.info("🔍 VERIFICANDO TRMs FALTANTES AL INICIAR SERVIDOR")
        logger.info("=" * 60)
        
        from app.services.trm_service import trm_service
        
        # Verificar últimos 30 días para recuperar períodos largos de inactividad
        logger.info("📅 Revisando últimos 30 días para TRMs faltantes...")
        resultado = trm_service.verificar_trms_faltantes(days_back=30)
        
        if resultado["success"]:
            logger.info("")
            logger.info("📊 RESUMEN DE RECUPERACIÓN DE TRMs:")
            logger.info(f"   ✅ Fechas faltantes encontradas: {resultado['missing_count']}")
            logger.info(f"   ✅ TRMs actualizadas exitosamente: {resultado['updated_count']}")
            logger.info(f"   ❌ Actualizaciones fallidas: {resultado['failed_count']}")
            
            if resultado["updated_count"] > 0:
                logger.info(f"   🎉 Se recuperaron {resultado['updated_count']} TRMs faltantes")
            
            if resultado["errors"]:
                logger.warning("")
                logger.warning("⚠️ Algunos TRMs no se pudieron obtener:")
                for error in resultado["errors"][:5]:  # Mostrar solo primeros 5 errores
                    logger.warning(f"   - {error}")
                if len(resultado["errors"]) > 5:
                    logger.warning(f"   ... y {len(resultado['errors']) - 5} errores más")
        else:
            logger.error(f"❌ Error en verificación: {resultado.get('error', 'Error desconocido')}")
        
        logger.info("=" * 60)
        logger.info("✅ VERIFICACIÓN DE TRMs COMPLETADA")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error en verificación de TRM: {e}")
        logger.info("⚠️ El servidor continuará sin verificación de TRM")

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 INICIANDO SERVIDOR FASTAPI - SISTEMA DE FLUJO DE CAJA")
    print("=" * 70)
    print()
    print("📊 Dashboard disponible en: http://localhost:8000/docs")
    print("🔗 API Base URL: http://localhost:8000/api/v1")
    print("⏹️  Presiona Ctrl+C para detener el servidor")
    print()
    print("=" * 70)
    
    # Verificar TRMs antes de iniciar el servidor
    verificar_trm_startup()
    print()
    
    print("=" * 70)
    print("✅ SERVIDOR LISTO - Aceptando peticiones")
    print("=" * 70)
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
