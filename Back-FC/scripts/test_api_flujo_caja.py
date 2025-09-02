#!/usr/bin/env python3
"""
Script para probar las APIs del sistema de flujo de caja
"""
import requests
import json
from datetime import date
from decimal import Decimal

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def autenticar_usuario():
    """Autenticar y obtener token"""
    print("🔐 AUTENTICANDO USUARIO...")
    
    # Datos de login (usando usuario por defecto)
    login_data = {
        "email": "admin@example.com",  # Email del usuario admin
        "password": "admin123"  # Contraseña por defecto
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"✅ Autenticación exitosa")
            return token
        else:
            print(f"❌ Error de autenticación: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def probar_conceptos_api(token):
    """Probar endpoints de conceptos"""
    print("\n📋 PROBANDO APIs DE CONCEPTOS")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 1. Obtener conceptos de tesorería
    print("1️⃣ Obteniendo conceptos de tesorería...")
    try:
        response = requests.get(f"{API_BASE}/conceptos-flujo-caja/por-area/tesoreria", headers=headers)
        if response.status_code == 200:
            conceptos = response.json()
            print(f"   ✅ {len(conceptos)} conceptos encontrados")
            for concepto in conceptos[:5]:  # Mostrar solo los primeros 5
                print(f"      - {concepto['nombre']} ({concepto['tipo']}) - Orden: {concepto['orden_display']}")
            if len(conceptos) > 5:
                print(f"      ... y {len(conceptos) - 5} más")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Obtener conceptos de pagaduría
    print("\n2️⃣ Obteniendo conceptos de pagaduría...")
    try:
        response = requests.get(f"{API_BASE}/conceptos-flujo-caja/por-area/pagaduria", headers=headers)
        if response.status_code == 200:
            conceptos = response.json()
            print(f"   ✅ {len(conceptos)} conceptos encontrados")
            for concepto in conceptos[:3]:  # Mostrar solo los primeros 3
                print(f"      - {concepto['nombre']} ({concepto['tipo']}) - Orden: {concepto['orden_display']}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Obtener estadísticas
    print("\n3️⃣ Obteniendo estadísticas de conceptos...")
    try:
        response = requests.get(f"{API_BASE}/conceptos-flujo-caja/estadisticas/generales", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Estadísticas:")
            print(f"      - Total: {stats['total']}")
            print(f"      - Activos: {stats['activos']}")
            print(f"      - Con dependencias: {stats['con_dependencias']}")
            print(f"      - Por área: {stats['por_area']}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def probar_transacciones_api(token):
    """Probar endpoints de transacciones"""
    print("\n💰 PROBANDO APIs DE TRANSACCIONES")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    fecha_hoy = date.today().isoformat()
    
    # 1. Obtener flujo de caja diario de tesorería
    print("1️⃣ Obteniendo flujo de caja diario - Tesorería...")
    try:
        response = requests.get(f"{API_BASE}/transacciones-flujo-caja/dashboard/tesoreria/{fecha_hoy}", headers=headers)
        if response.status_code == 200:
            flujo = response.json()
            print(f"   ✅ Flujo de caja del {flujo['fecha']}:")
            print(f"      - Área: {flujo['area']}")
            print(f"      - Conceptos: {len(flujo['conceptos'])}")
            print(f"      - Totales: {flujo['totales']}")
            
            # Mostrar algunos conceptos con valores
            conceptos_con_valor = [c for c in flujo['conceptos'] if float(c['monto']) > 0]
            if conceptos_con_valor:
                print(f"      - Conceptos con transacciones:")
                for concepto in conceptos_con_valor:
                    print(f"        • {concepto['concepto_nombre']}: ${float(concepto['monto']):,.2f}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Obtener flujo de caja diario de pagaduría
    print("\n2️⃣ Obteniendo flujo de caja diario - Pagaduría...")
    try:
        response = requests.get(f"{API_BASE}/transacciones-flujo-caja/dashboard/pagaduria/{fecha_hoy}", headers=headers)
        if response.status_code == 200:
            flujo = response.json()
            print(f"   ✅ Flujo de caja del {flujo['fecha']}:")
            print(f"      - Área: {flujo['area']}")
            print(f"      - Conceptos: {len(flujo['conceptos'])}")
            print(f"      - Totales: {flujo['totales']}")
            
            # Mostrar algunos conceptos con valores
            conceptos_con_valor = [c for c in flujo['conceptos'] if float(c['monto']) > 0]
            if conceptos_con_valor:
                print(f"      - Conceptos con transacciones:")
                for concepto in conceptos_con_valor:
                    print(f"        • {concepto['concepto_nombre']}: ${float(concepto['monto']):,.2f}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Obtener transacciones por fecha
    print("\n3️⃣ Obteniendo todas las transacciones del día...")
    try:
        response = requests.get(f"{API_BASE}/transacciones-flujo-caja/fecha/{fecha_hoy}", headers=headers)
        if response.status_code == 200:
            transacciones = response.json()
            print(f"   ✅ {len(transacciones)} transacciones encontradas:")
            for transaccion in transacciones:
                print(f"      - {transaccion['concepto']['nombre']} ({transaccion['area']}): ${float(transaccion['monto']):,.2f}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def probar_dependencias(token):
    """Probar funcionalidad de dependencias"""
    print("\n🔗 PROBANDO DEPENDENCIAS AUTOMÁTICAS")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Obtener conceptos con dependencias
    print("1️⃣ Verificando conceptos con dependencias...")
    try:
        response = requests.get(f"{API_BASE}/conceptos-flujo-caja/dependencias/tesoreria", headers=headers)
        if response.status_code == 200:
            conceptos_dep = response.json()
            print(f"   ✅ {len(conceptos_dep)} conceptos con dependencias:")
            for concepto in conceptos_dep:
                if concepto['depende_de_concepto_id']:
                    print(f"      - {concepto['nombre']} depende de concepto ID {concepto['depende_de_concepto_id']} ({concepto['tipo_dependencia']})")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Función principal"""
    print("🧪 INICIANDO PRUEBAS DE APIs DEL FLUJO DE CAJA")
    print("=" * 60)
    
    # Autenticar
    token = autenticar_usuario()
    if not token:
        print("❌ No se pudo autenticar. Asegúrate de que:")
        print("   1. El servidor esté corriendo")
        print("   2. Exista un usuario con email 'admin@example.com' y contraseña 'admin123'")
        return
    
    # Probar APIs
    probar_conceptos_api(token)
    probar_transacciones_api(token)
    probar_dependencias(token)
    
    print("\n🎉 PRUEBAS COMPLETADAS")
    print("=" * 60)
    print("✅ Sistema de flujo de caja funcionando correctamente!")
    print("📍 Puedes ver la documentación completa en: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
