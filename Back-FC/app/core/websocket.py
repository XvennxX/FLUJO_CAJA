"""
WebSocket Connection Manager
Maneja todas las conexiones WebSocket activas para actualizaciones en tiempo real
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Gestiona conexiones WebSocket para notificaciones en tiempo real"""
    
    def __init__(self):
        # Lista de conexiones WebSocket activas
        self.active_connections: List[WebSocket] = []
        
        # Diccionario para rastrear usuarios por conexión
        self.user_connections: Dict[WebSocket, int] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int = None):
        """Conectar un nuevo WebSocket y registrar el usuario"""
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            
            if user_id:
                self.user_connections[websocket] = user_id
            
            logger.info(f"🔗 Nueva conexión WebSocket establecida. Usuario: {user_id}")
            logger.info(f"📊 Total conexiones activas: {len(self.active_connections)}")
            
        except Exception as e:
            logger.error(f"❌ Error conectando WebSocket: {e}")
    
    def disconnect(self, websocket: WebSocket):
        """Desconectar WebSocket y limpiar registros"""
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            
            user_id = self.user_connections.pop(websocket, "Unknown")
            
            logger.info(f"🔌 Conexión WebSocket cerrada. Usuario: {user_id}")
            logger.info(f"📊 Total conexiones activas: {len(self.active_connections)}")
            
        except Exception as e:
            logger.error(f"❌ Error desconectando WebSocket: {e}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Enviar mensaje a una conexión específica"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje personal: {e}")
            self.disconnect(websocket)
    
    async def broadcast_update(self, message: dict):
        """
        Enviar actualización a todas las conexiones activas
        Limpia automáticamente conexiones cerradas
        """
        if not self.active_connections:
            logger.info("📡 No hay conexiones activas para enviar actualización")
            return
            
        # Lista de conexiones a remover (cerradas)
        disconnected = []
        
        # Agregar timestamp al mensaje
        message["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"📡 Enviando actualización a {len(self.active_connections)} conexiones")
        logger.info(f"📋 Mensaje: {message}")
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"⚠️ Conexión cerrada detectada: {e}")
                disconnected.append(connection)
        
        # Remover conexiones cerradas
        for conn in disconnected:
            self.disconnect(conn)
        
        success_count = len(self.active_connections) - len(disconnected)
        logger.info(f"✅ Actualización enviada exitosamente a {success_count} conexiones")
    
    async def broadcast_to_area(self, message: dict, area: str):
        """Enviar actualización solo a usuarios de un área específica"""
        message["area_filter"] = area
        await self.broadcast_update(message)
    
    def get_connection_stats(self) -> dict:
        """Obtener estadísticas de conexiones"""
        return {
            "total_connections": len(self.active_connections),
            "registered_users": len(self.user_connections),
            "anonymous_connections": len(self.active_connections) - len(self.user_connections)
        }

# Instancia global del manager
websocket_manager = ConnectionManager()