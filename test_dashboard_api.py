#!/usr/bin/env python3
"""
Script para probar el endpoint de transacciones y verificar auto-cálculos
"""

import requests
import json
from datetime import date

def test_dashboard_api():
    base_url = "http://localhost:8000"
    
    # Fecha actual
    fecha_actual = date.today().strftime('%Y-%m-%d')
    
    # Primero, autenticarse
    print("🔐 Iniciando sesión...")
    login_data = {
        "email": "maria.lopez@flujo.com",
        "password": "tesoreria123"
    }
    
    try:
        # Login
        login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
            
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            print("❌ No se recibió token de acceso")
            return
            
        print("✅ Login exitoso")
        
        # Headers con autenticación
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está el backend corriendo en puerto 8000?")
        return
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return
    
    try:
        # Test 1: Verificar que el endpoint de transacciones responda
        print("🔍 Probando endpoint de transacciones...")
        
        # Probar diferentes rutas posibles
        possible_routes = [
            f"{base_url}/api/v1/api/transacciones-flujo-caja/fecha/{fecha_actual}",
            f"{base_url}/api/v1/api/transacciones-flujo-caja/dashboard/tesoreria/{fecha_actual}"
        ]
        
        response = None
        working_route = None
        
        for route in possible_routes:
            try:
                test_response = requests.get(
                    route,
                    headers=headers,
                    timeout=5
                )
                print(f"Probando {route}: Status {test_response.status_code}")
                
                if test_response.status_code == 200:
                    response = test_response
                    working_route = route
                    break
            except Exception as e:
                print(f"Error probando {route}: {e}")
                continue
        
        if not response:
            print("❌ No se encontró ruta válida para transacciones")
            # Intentar con la primera ruta para mostrar el error
            response = requests.get(possible_routes[0], params={"fecha": fecha_actual}, headers=headers, timeout=10)
        
        if response.status_code == 200:
            transacciones = response.json()
            print(f"✅ Endpoint respondió correctamente en: {working_route}")
            print(f"✅ Transacciones encontradas: {len(transacciones)}")
            
            # Verificar auto-cálculos
            conceptos_auto = [4, 50, 51]  # SALDO NETO INICIAL, SUB-TOTAL TESORERÍA, SALDO FINAL
            auto_calculadas = [t for t in transacciones if t.get('concepto_id') in conceptos_auto]
            
            print(f"📊 Transacciones auto-calculadas encontradas: {len(auto_calculadas)}")
            
            # Agrupar por concepto
            for concepto_id in conceptos_auto:
                concepto_transacciones = [t for t in auto_calculadas if t.get('concepto_id') == concepto_id]
                if concepto_transacciones:
                    concepto_nombre = concepto_transacciones[0].get('concepto', {}).get('nombre', f'Concepto {concepto_id}')
                    print(f"  - {concepto_nombre}: {len(concepto_transacciones)} transacciones")
                    
                    # Mostrar ejemplo de una cuenta
                    if concepto_transacciones:
                        ejemplo = concepto_transacciones[0]
                        print(f"    Ejemplo - Cuenta {ejemplo.get('cuenta_id')}: ${ejemplo.get('monto', 0)}")
            
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está el backend corriendo en puerto 8000?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

    # Test 2: Verificar endpoint de conceptos
    try:
        print("\n🔍 Probando endpoint de conceptos...")
        response = requests.get(f"{base_url}/api/v1/conceptos-flujo-caja", headers=headers, timeout=10)
        
        if response.status_code == 200:
            conceptos = response.json()
            auto_conceptos = [c for c in conceptos if c.get('id') in [4, 50, 51]]
            print(f"✅ Conceptos auto-calculados configurados: {len(auto_conceptos)}")
            for concepto in auto_conceptos:
                print(f"  - ID {concepto.get('id')}: {concepto.get('nombre')}")
                if concepto.get('formula_dependencia'):
                    print(f"    Fórmula: {concepto.get('formula_dependencia')}")
        else:
            print(f"❌ Error en endpoint de conceptos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en endpoint de conceptos: {e}")

    print(f"\n🎉 Verificación completada para la fecha: {fecha_actual}")
    print("💡 Ahora puedes verificar el dashboard en: http://localhost:5001")

if __name__ == "__main__":
    test_dashboard_api()
