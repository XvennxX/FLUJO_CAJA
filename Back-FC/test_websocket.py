#!/usr/bin/env python3
"""
Script de prueba para verificar que el WebSocket funciona correctamente
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket_connection():
    """Probar la conexión WebSocket"""
    
    print("🔗 Conectando al WebSocket del servidor...")
    
    try:
        # Conectar al WebSocket (ajusta la URL según tu configuración)
        uri = "ws://localhost:8000/api/v1/api/transacciones-flujo-caja/ws"
        
        async with websockets.connect(uri) as websocket:
            print("✅ Conexión WebSocket establecida exitosamente!")
            
            # Enviar un ping
            ping_message = {
                "type": "ping",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(ping_message))
            print(f"📤 Mensaje ping enviado: {ping_message}")
            
            # Escuchar mensajes por 30 segundos
            print("👂 Escuchando mensajes por 30 segundos...")
            print("   (Modifica una transacción desde el frontend para ver la notificación)")
            
            try:
                # Escuchar con timeout de 30 segundos
                message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                
                try:
                    data = json.loads(message)
                    print(f"📨 Mensaje recibido: {json.dumps(data, indent=2)}")
                    
                    if data.get("type") == "pong":
                        print("✅ Respuesta pong recibida - conexión activa")
                    elif data.get("type") == "transaccion_updated":
                        print("🔄 ¡Notificación de transacción actualizada recibida!")
                        print(f"   - ID: {data.get('transaccion_id')}")
                        print(f"   - Área: {data.get('area')}")
                        print(f"   - Dependencias actualizadas: {data.get('total_dependencias_actualizadas')}")
                    elif data.get("type") == "connection_established":
                        print("🎉 Mensaje de bienvenida recibido")
                        
                except json.JSONDecodeError:
                    print(f"📨 Mensaje recibido (texto): {message}")
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout - no se recibieron mensajes en 30 segundos")
                print("   Esto es normal si no hay actividad en las transacciones")
                
    except websockets.exceptions.ConnectionRefused:
        print("❌ Error: No se pudo conectar al WebSocket")
        print("   Asegúrate de que el servidor FastAPI esté ejecutándose en localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    print("🏁 Prueba completada")
    return True

async def test_multiple_messages():
    """Probar múltiples mensajes"""
    
    print("\n🔄 Probando múltiples mensajes...")
    
    try:
        uri = "ws://localhost:8000/api/v1/api/transacciones-flujo-caja/ws"
        
        async with websockets.connect(uri) as websocket:
            
            # Enviar varios pings
            for i in range(3):
                ping_message = {
                    "type": "ping",
                    "sequence": i + 1,
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(ping_message))
                print(f"📤 Ping {i+1} enviado")
                
                # Esperar respuesta
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    if data.get("type") == "pong":
                        print(f"📨 Pong {i+1} recibido ✅")
                except asyncio.TimeoutError:
                    print(f"⏰ Timeout en pong {i+1}")
                
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"❌ Error en prueba múltiples mensajes: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas WebSocket para Flujo de Caja")
    print("=" * 50)
    
    # Ejecutar pruebas
    asyncio.run(test_websocket_connection())
    asyncio.run(test_multiple_messages())
    
    print("\n" + "=" * 50)
    print("📋 INSTRUCCIONES PARA PRUEBA COMPLETA:")
    print("1. Asegúrate de que el servidor FastAPI esté ejecutándose")
    print("2. Ejecuta este script en una terminal")
    print("3. En otra ventana, abre el frontend")
    print("4. Modifica una transacción desde el frontend")
    print("5. Deberías ver la notificación en este script")
    print("\n✨ Si todo funciona, el WebSocket está listo para producción!")