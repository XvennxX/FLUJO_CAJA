#!/usr/bin/env python3
"""
Script para probar el sistema de WebSocket en tiempo real
Simula la modificación de una transacción para verificar actualizaciones automáticas
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Simular token de autenticación (usar token real del localStorage)
# Para efectos de prueba, usaremos un header básico
headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer tu_token_aqui"  # Agregar token real si es necesario
}

def test_websocket_updates():
    """Prueba las actualizaciones en tiempo real via WebSocket"""
    
    print("🚀 Iniciando prueba de WebSocket...")
    
    # 1. Obtener fecha actual
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 Fecha de prueba: {fecha_hoy}")
    
    # 2. Listar transacciones existentes en Tesorería
    print("\n📋 Obteniendo transacciones de Tesorería...")
    try:
        response = requests.get(
            f"{API_BASE}/api/transacciones-flujo-caja/fecha/{fecha_hoy}?area=tesoreria",
            headers=headers
        )
        
        if response.status_code == 200:
            transacciones = response.json()
            print(f"✅ Encontradas {len(transacciones)} transacciones en Tesorería")
            
            if transacciones:
                # Tomar la primera transacción para modificar
                transaccion = transacciones[0]
                transaccion_id = transaccion['id']
                monto_original = transaccion['monto']
                nuevo_monto = monto_original + 1000  # Incrementar en 1000
                
                print(f"🎯 Seleccionada transacción ID: {transaccion_id}")
                print(f"💰 Monto original: {monto_original}")
                print(f"💰 Nuevo monto: {nuevo_monto}")
                
                # 3. Modificar la transacción (esto debería disparar WebSocket)
                print(f"\n🔄 Modificando transacción...")
                
                update_data = {
                    "monto": nuevo_monto,
                    "descripcion": f"Prueba WebSocket - {datetime.now().strftime('%H:%M:%S')}"
                }
                
                response = requests.put(
                    f"{API_BASE}/api/transacciones-flujo-caja/{transaccion_id}",
                    headers=headers,
                    json=update_data
                )
                
                if response.status_code == 200:
                    print("✅ Transacción modificada exitosamente!")
                    print("📡 Mensaje WebSocket debería haberse enviado a todos los dashboards conectados")
                    print("\n🎯 PRUEBA MANUAL:")
                    print("1. Abre el dashboard de Pagaduría en el navegador")
                    print("2. Deberías ver una notificación verde de actualización automática")
                    print("3. Los datos deberían actualizarse sin necesidad de F5")
                    
                    # Revertir cambio después de 10 segundos
                    print(f"\n⏰ En 10 segundos revertiremos el cambio...")
                    import time
                    time.sleep(10)
                    
                    revert_data = {
                        "monto": monto_original,
                        "descripcion": "Cambio revertido automáticamente"
                    }
                    
                    response = requests.put(
                        f"{API_BASE}/api/transacciones-flujo-caja/{transaccion_id}",
                        headers=headers,
                        json=revert_data
                    )
                    
                    if response.status_code == 200:
                        print("✅ Cambio revertido exitosamente!")
                        print("📡 Segundo mensaje WebSocket enviado")
                    else:
                        print(f"❌ Error revirtiendo cambio: {response.status_code}")
                        print(response.text)
                        
                else:
                    print(f"❌ Error modificando transacción: {response.status_code}")
                    print(response.text)
            else:
                print("⚠️  No hay transacciones para modificar")
                print("💡 Puedes crear una transacción primero en el dashboard")
        else:
            print(f"❌ Error obteniendo transacciones: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al backend. ¿Está corriendo en el puerto 8000?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_websocket_updates()