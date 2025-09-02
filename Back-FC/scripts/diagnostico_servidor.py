#!/usr/bin/env python3
"""
Script simple para verificar conectividad con las APIs
"""
import requests
import json

def verificar_servidor():
    """Verificar que el servidor esté corriendo"""
    print("🔍 VERIFICANDO SERVIDOR...")
    
    try:
        # Verificar endpoint de salud
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor corriendo: {data['service']} v{data['version']}")
            return True
        else:
            print(f"❌ Error en endpoint de salud: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def verificar_endpoints():
    """Verificar endpoints disponibles"""
    print("\n📋 VERIFICANDO ENDPOINTS DISPONIBLES...")
    
    try:
        # Obtener documentación OpenAPI
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            openapi = response.json()
            paths = openapi.get("paths", {})
            
            print(f"✅ {len(paths)} endpoints disponibles:")
            
            # Filtrar endpoints de flujo de caja
            flujo_caja_endpoints = [path for path in paths.keys() if "flujo" in path.lower()]
            
            if flujo_caja_endpoints:
                print(f"\n🔧 Endpoints de Flujo de Caja ({len(flujo_caja_endpoints)}):")
                for endpoint in flujo_caja_endpoints:
                    methods = list(paths[endpoint].keys())
                    print(f"   - {endpoint} [{', '.join(methods).upper()}]")
            else:
                print("⚠️ No se encontraron endpoints de flujo de caja")
                
            # Mostrar algunos endpoints principales
            auth_endpoints = [path for path in paths.keys() if "auth" in path.lower()]
            if auth_endpoints:
                print(f"\n🔐 Endpoints de Autenticación ({len(auth_endpoints)}):")
                for endpoint in auth_endpoints:
                    methods = list(paths[endpoint].keys())
                    print(f"   - {endpoint} [{', '.join(methods).upper()}]")
                    
        else:
            print(f"❌ Error obteniendo documentación: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def probar_acceso_sin_auth():
    """Probar acceso a endpoints sin autenticación"""
    print("\n🔓 PROBANDO ACCESO SIN AUTENTICACIÓN...")
    
    endpoints_publicos = [
        "/",
        "/health", 
        "/docs",
        "/openapi.json"
    ]
    
    for endpoint in endpoints_publicos:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}")
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"   {status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Error - {e}")

def main():
    """Función principal"""
    print("🔧 DIAGNÓSTICO DEL SERVIDOR DE FLUJO DE CAJA")
    print("=" * 60)
    
    if not verificar_servidor():
        print("❌ El servidor no está respondiendo correctamente")
        return
    
    verificar_endpoints()
    probar_acceso_sin_auth()
    
    print("\n📍 PRÓXIMOS PASOS:")
    print("   1. Revisar la documentación en: http://localhost:8000/docs")
    print("   2. Probar endpoints desde la interfaz interactiva")
    print("   3. Verificar logs del servidor para errores de autenticación")

if __name__ == "__main__":
    main()
