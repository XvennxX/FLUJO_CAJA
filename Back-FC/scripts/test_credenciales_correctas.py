#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar autenticación con credenciales conocidas
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login_and_endpoints():
    """Probar login y endpoints con credenciales correctas"""
    
    # Usuarios con credenciales correctas
    usuarios = [
        ("carlos.gomez@flujo.com", "admin123", "Carlos (Admin)"),
        ("maria.lopez@flujo.com", "tesoreria123", "María (Tesorería)"),
        ("javier.ruiz@flujo.com", "pagaduria123", "Javier (Pagaduría)"),
        ("laura.martinez@flujo.com", "mesa123", "Laura (Mesa)")
    ]
    
    print("🧪 PROBANDO AUTENTICACIÓN CON CREDENCIALES CORRECTAS")
    print("=" * 60)
    
    successful_login = None
    
    for email, password, nombre in usuarios:
        print(f"\n🔐 Probando {nombre}: {email}")
        
        login_data = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Login exitoso!")
                print(f"   Usuario: {data.get('user', {}).get('nombre', 'N/A')}")
                print(f"   Rol: {data.get('user', {}).get('rol', 'N/A')}")
                print(f"   Token: {data.get('access_token', 'N/A')[:30]}...")
                
                # Guardar para pruebas posteriores
                if not successful_login:
                    successful_login = {
                        "token": data.get("access_token"),
                        "user": data.get("user"),
                        "credentials": (email, password, nombre)
                    }
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Detalle: {error_data.get('detail', response.text)}")
                except:
                    print(f"   Texto: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
    
    # Probar endpoints protegidos con el primer login exitoso
    if successful_login:
        print(f"\n🔒 PROBANDO ENDPOINTS PROTEGIDOS...")
        test_protected_endpoints(successful_login)
    else:
        print(f"\n❌ No se pudo autenticar con ningún usuario")

def test_protected_endpoints(login_info):
    """Probar endpoints protegidos"""
    token = login_info["token"]
    user = login_info["user"]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints_to_test = [
        ("/api/v1/auth/me", "GET", "Información del usuario"),
        ("/api/v1/api/conceptos-flujo-caja/", "GET", "Lista de conceptos"),
        ("/api/v1/api/conceptos-flujo-caja/por-area/tesoreria", "GET", "Conceptos de tesorería"),
        ("/api/v1/api/conceptos-flujo-caja/por-area/pagaduria", "GET", "Conceptos de pagaduría"),
        ("/api/v1/api/transacciones-flujo-caja/fecha/2025-08-26", "GET", "Transacciones de hoy"),
    ]
    
    print(f"   Usuario autenticado: {user.get('nombre')} ({user.get('rol')})")
    print("-" * 50)
    
    for endpoint, method, description in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"   {status_icon} {description}")
            print(f"      {method} {endpoint}")
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"      Resultados: {len(data)} elementos")
                    elif isinstance(data, dict):
                        print(f"      Datos: {len(data)} campos")
                except:
                    print(f"      Respuesta: {len(response.text)} caracteres")
            else:
                try:
                    error_data = response.json()
                    print(f"      Error: {error_data.get('detail', 'Error desconocido')}")
                except:
                    print(f"      Error: {response.text[:100]}...")
            
            print()
            
        except Exception as e:
            print(f"   ❌ {description}")
            print(f"      Error de conexión: {e}")
            print()

def test_conceptos_management():
    """Probar gestión de conceptos con admin"""
    print(f"\n🔧 PROBANDO GESTIÓN DE CONCEPTOS...")
    
    # Login como admin
    admin_login = {
        "email": "carlos.gomez@flujo.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=admin_login,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print("   ❌ No se pudo autenticar como admin")
            return
        
        token = response.json().get("access_token")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Obtener estadísticas generales
        stats_response = requests.get(
            f"{BASE_URL}/api/v1/api/conceptos-flujo-caja/estadisticas/generales",
            headers=headers
        )
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   ✅ Estadísticas generales:")
            print(f"      Total conceptos: {stats.get('total_conceptos', 0)}")
            print(f"      Tesorería: {stats.get('conceptos_tesoreria', 0)}")
            print(f"      Pagaduría: {stats.get('conceptos_pagaduria', 0)}")
            print(f"      Activos: {stats.get('conceptos_activos', 0)}")
        else:
            print(f"   ❌ Error obteniendo estadísticas: {stats_response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_login_and_endpoints()
    test_conceptos_management()
