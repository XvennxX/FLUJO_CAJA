import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OptimizedTransactionService:
    """Servicio optimizado para transacciones con procesamiento asíncrono"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="transaction_deps")
    
    async def procesar_dependencias_async(
        self,
        fecha,
        concepto_id: int,
        cuenta_id: int,
        user_id: int,
        db_session
    ):
        """Procesa dependencias de forma asíncrona"""
        try:
            # Usar un pequeño delay para permitir que la respuesta HTTP se envíe primero
            await asyncio.sleep(0.1)
            
            logger.info(f"� ASYNC: Procesando dependencias para concepto {concepto_id}")
            
            # Importación dinámica para evitar dependencias circulares
            from ..services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
            
            # Crear nueva sesión de DB para el hilo de fondo
            from ..core.database import get_db
            db = next(get_db())
            
            try:
                dependencias_service = DependenciasFlujoCajaService(db)
                resultados = dependencias_service.procesar_dependencias_completas_ambos_dashboards(
                    fecha=fecha,
                    concepto_modificado_id=concepto_id,
                    cuenta_id=cuenta_id,
                    compania_id=1,
                    usuario_id=user_id
                )
                
                total_updates = (
                    len(resultados.get("tesoreria", [])) + 
                    len(resultados.get("pagaduria", [])) + 
                    len(resultados.get("cross_dashboard", []))
                )
                
                logger.info(f"✅ ASYNC: {total_updates} dependencias procesadas correctamente")
                
                # Notificación WebSocket opcional
                try:
                    from ..core.websocket import websocket_manager
                    await websocket_manager.broadcast_update({
                        "type": "dependencias_procesadas",
                        "concepto_id": concepto_id,
                        "fecha": fecha.isoformat() if hasattr(fecha, 'isoformat') else str(fecha),
                        "total_actualizaciones": total_updates,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as ws_error:
                    logger.warning(f"⚠️ Error en notificación WebSocket: {ws_error}")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error en procesamiento asíncrono de dependencias: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")

# Instancia global del servicio optimizado
optimized_service = OptimizedTransactionService()