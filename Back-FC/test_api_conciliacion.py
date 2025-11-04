#!/usr/bin/env python3
"""
Script para probar la API de conciliación directamente
"""
import requests
import json
from datetime import date

def test_api_conciliacion():
    """Probar la API de conciliación"""
    
    print("=" * 60)
    print("PROBANDO API DE CONCILIACIÓN")
    print("=" * 60)
    
    # 1. Primero hacer login para obtener token
    print("\n1. HACIENDO LOGIN...")
    
    login_data = {
        "username": "admin@bolivar.com",  # Cambia por un usuario válido
        "password": "admin123"  # Cambia por la contraseña correcta
    }
    
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"   ✅ Login exitoso. Token obtenido.")
            
            # 2. Probar endpoint de conciliación
            print(f"\n2. PROBANDO ENDPOINT DE CONCILIACIÓN...")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            conciliacion_data = {
                "fecha": "2025-11-04"
            }
            
            response = requests.post(
                "http://localhost:8000/api/v1/conciliacion/fecha",
                json=conciliacion_data,
                headers=headers
            )
            
            print(f"   📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Respuesta exitosa:")
                print(f"   📅 Fecha: {result.get('fecha')}")
                print(f"   🏢 Empresas encontradas: {len(result.get('empresas', []))}")
                
                if result.get('empresas'):
                    print(f"\n   DETALLE DE EMPRESAS:")
                    for empresa in result['empresas'][:3]:  # Mostrar solo las primeras 3
                        print(f"     • {empresa.get('compania', {}).get('nombre', 'N/A')}")
                        print(f"       - Pagaduría: ${empresa.get('total_pagaduria', 0):.2f}")
                        print(f"       - Tesorería: ${empresa.get('total_tesoreria', 0):.2f}")
                        print(f"       - Total: ${empresa.get('total_calculado', 0):.2f}")
                        print(f"       - Estado: {empresa.get('estado', 'N/A')}")
                else:
                    print(f"   ❌ No se encontraron empresas en la respuesta")
                    
            else:
                print(f"   ❌ Error en la API: {response.text}")
                
        else:
            print(f"   ❌ Error en login: {login_response.text}")
            print(f"   💡 Verifica las credenciales en el script")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        print(f"   💡 Verifica que el backend esté corriendo en http://localhost:8000")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_api_conciliacion()