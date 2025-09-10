#!/usr/bin/env python3
"""
Test del endpoint API modificado para auto-inicialización automática
Simula el comportamiento real cuando un usuario accede a una fecha nueva
"""

import requests
import json
from datetime import datetime

def test_api_auto_inicializacion():
    """Test del endpoint API con auto-inicialización"""
    
    base_url = "http://localhost:8000"  # Ajustar según tu configuración
    
    # Headers básicos
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("=== TEST API AUTO-INICIALIZACIÓN ===")
    
    # 1. Test con día 10 (debería auto-crear SALDO INICIAL)
    fecha_test = "2025-09-10"
    print(f"\n🔍 Probando endpoint para fecha: {fecha_test}")
    
    try:
        # Llamar al endpoint de transacciones
        url = f"{base_url}/api/v1/api/transacciones-flujo-caja/fecha/{fecha_test}"
        
        print(f"   📡 GET {url}")
        
        response = requests.get(url, headers=headers)
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta exitosa")
            print(f"   📝 Total transacciones: {len(data.get('transacciones', []))}")
            
            # Buscar SALDO INICIAL en las transacciones
            saldo_inicial = None
            for trans in data.get('transacciones', []):
                if trans.get('concepto_nombre') == 'SALDO INICIAL':
                    saldo_inicial = trans
                    break
            
            if saldo_inicial:
                print(f"   🎉 SALDO INICIAL encontrado:")
                print(f"      💰 Monto: ${saldo_inicial.get('monto')}")
                print(f"      🏦 Cuenta: {saldo_inicial.get('cuenta_id')}")
                print(f"      📋 Descripción: {saldo_inicial.get('descripcion')}")
            else:
                print(f"   ❌ No se encontró SALDO INICIAL")
                
        else:
            print(f"   ❌ Error en la respuesta: {response.status_code}")
            print(f"   📄 Detalle: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  No se pudo conectar al servidor en {base_url}")
        print(f"   💡 Asegúrate de que el servidor esté ejecutándose")
        print(f"   🔧 Comando: cd Back-FC && python run_server.py")
        
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")

def test_multiples_fechas():
    """Test con múltiples fechas para ver el comportamiento continuado"""
    
    fechas_test = [
        "2025-09-10",
        "2025-09-11", 
        "2025-09-12"
    ]
    
    print(f"\n🔄 === TEST MÚLTIPLES FECHAS ===")
    
    for fecha in fechas_test:
        print(f"\n📅 Probando fecha: {fecha}")
        test_fecha_especifica(fecha)

def test_fecha_especifica(fecha):
    """Test una fecha específica"""
    
    base_url = "http://localhost:8000"
    
    try:
        url = f"{base_url}/api/v1/api/transacciones-flujo-caja/fecha/{fecha}"
        response = requests.get(url, headers={"Accept": "application/json"})
        
        if response.status_code == 200:
            data = response.json()
            transacciones = data.get('transacciones', [])
            
            saldo_inicial = [t for t in transacciones if t.get('concepto_nombre') == 'SALDO INICIAL']
            
            if saldo_inicial:
                print(f"   ✅ SALDO INICIAL: ${saldo_inicial[0].get('monto')}")
            else:
                print(f"   ❌ Sin SALDO INICIAL")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  Servidor no disponible")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando test del API endpoint...")
    print("📋 Este test verifica que el endpoint auto-inicialice SALDO INICIAL")
    print("🔧 Asegúrate de que el servidor esté corriendo: python run_server.py")
    print()
    
    test_api_auto_inicializacion()
    
    # Test adicional con múltiples fechas
    respuesta = input("\n¿Probar múltiples fechas? (y/n): ")
    if respuesta.lower() == 'y':
        test_multiples_fechas()
    
    print("\n🎉 Test completado!")
    print("💡 Si el SALDO INICIAL se creó automáticamente, ¡la integración funciona!")
