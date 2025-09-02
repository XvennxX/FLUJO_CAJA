#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la autenticación del sistema de flujo de caja de forma detallada
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_server_health():
    """Verificar que el servidor esté funcionando"""
    print("🔍 VERIFICANDO ESTADO DEL SERVIDOR...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"✅ Servidor funcionando: {response.json()}")
            return True
        else:
            print(f"❌ Error en servidor: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se pudo conectar al servidor: {e}")
        return False

def get_all_users():
    """Obtener información de usuarios para testing"""
    print("\n🔍 OBTENIENDO USUARIOS PARA TESTING...")
    try:
        # Intentar obtener usuarios desde el endpoint de usuarios (si existe y no está protegido)
        response = requests.get(f"{BASE_URL}/api/v1/users/")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Usuarios disponibles: {len(users)}")
            for user in users[:3]:  # Solo mostrar los primeros 3
                print(f"   - {user.get('nombre', 'N/A')} ({user.get('email', 'N/A')}) - {user.get('rol', 'N/A')}")
            return users
        else:
            print(f"⚠️ No se pudieron obtener usuarios: {response.status_code}")
            return []
    except Exception as e:
        print(f"⚠️ Error obteniendo usuarios: {e}")
        return []

def test_login_with_credentials(email, password):
    """Probar login con credenciales específicas"""
    print(f"\n🔐 PROBANDO LOGIN CON: {email}")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers=headers
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Login exitoso!")
            print(f"   Token: {token_data.get('access_token', 'N/A')[:50]}...")
            print(f"   Usuario: {token_data.get('user', {}).get('nombre', 'N/A')}")
            print(f"   Rol: {token_data.get('user', {}).get('rol', 'N/A')}")
            return token_data.get('access_token')
        else:
            print(f"   ❌ Login fallido!")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Error texto: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error en petición: {e}")
        return None

def test_protected_endpoint(token):
    """Probar un endpoint protegido"""
    if not token:
        print("\n❌ No hay token para probar endpoints protegidos")
        return
        
    print(f"\n🔒 PROBANDO ENDPOINT PROTEGIDO...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Probar el endpoint /me
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        print(f"   /auth/me - Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Usuario autenticado: {user_data.get('nombre', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
        # Probar endpoint de conceptos de flujo de caja
        response = requests.get(f"{BASE_URL}/api/v1/api/conceptos-flujo-caja/", headers=headers)
        print(f"   /conceptos-flujo-caja - Status: {response.status_code}")
        
        if response.status_code == 200:
            conceptos = response.json()
            print(f"   ✅ Conceptos obtenidos: {len(conceptos)}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error probando endpoints: {e}")

def main():
    print("🧪 TEST DETALLADO DE AUTENTICACIÓN")
    print("=" * 50)
    
    # 1. Verificar servidor
    if not test_server_health():
        sys.exit(1)
    
    # 2. Obtener usuarios disponibles
    users = get_all_users()
    
    # 3. Credenciales de prueba conocidas
    test_credentials = [
        ("mesa@bolivar.com", "mesa123"),
        ("tesoreria@bolivar.com", "tesoreria123"), 
        ("pagaduria@bolivar.com", "pagaduria123"),
        ("admin@bolivar.com", "admin123"),
    ]
    
    # Si tenemos usuarios de la base de datos, agregarlos
    if users:
        for user in users[:2]:  # Solo los primeros 2
            email = user.get('email')
            if email and email not in [cred[0] for cred in test_credentials]:
                # Usar una contraseña común para testing
                test_credentials.append((email, "123456"))
    
    # 4. Probar cada credencial
    successful_token = None
    for email, password in test_credentials:
        token = test_login_with_credentials(email, password)
        if token and not successful_token:
            successful_token = token
    
    # 5. Probar endpoints protegidos
    test_protected_endpoint(successful_token)
    
    print(f"\n📋 RESUMEN:")
    if successful_token:
        print("✅ Autenticación funcionando correctamente")
        print("✅ Sistema listo para usar")
    else:
        print("❌ Problemas con autenticación")
        print("🔧 Revisar credenciales o configuración del servidor")

if __name__ == "__main__":
    main()
