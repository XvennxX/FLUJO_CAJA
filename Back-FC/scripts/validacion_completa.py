#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script final de validación completa del sistema de flujo de caja
"""

import requests
import json
from datetime import datetime, date
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class FlujoCajaValidator:
    def __init__(self):
        self.token = None
        self.user_info = None
        
    def login(self, email: str, password: str) -> bool:
        """Hacer login y obtener token"""
        try:
            login_data = {"email": email, "password": password}
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_info = data.get("user")
                return True
            return False
        except Exception:
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Obtener headers con autorización"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_conceptos_endpoints(self) -> Dict[str, Any]:
        """Probar todos los endpoints de conceptos"""
        results = {}
        headers = self.get_headers()
        
        tests = [
            ("Lista completa", "GET", "/api/v1/api/conceptos-flujo-caja/"),
            ("Conceptos tesorería", "GET", "/api/v1/api/conceptos-flujo-caja/por-area/tesoreria"),
            ("Conceptos pagaduría", "GET", "/api/v1/api/conceptos-flujo-caja/por-area/pagaduria"),
            ("Dependencias tesorería", "GET", "/api/v1/api/conceptos-flujo-caja/dependencias/tesoreria"),
            ("Dependencias pagaduría", "GET", "/api/v1/api/conceptos-flujo-caja/dependencias/pagaduria"),
            ("Estadísticas", "GET", "/api/v1/api/conceptos-flujo-caja/estadisticas/generales"),
        ]
        
        for name, method, endpoint in tests:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                results[name] = {
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "data_count": len(response.json()) if response.status_code == 200 and isinstance(response.json(), list) else None
                }
            except Exception as e:
                results[name] = {"status": "error", "success": False, "error": str(e)}
        
        return results
    
    def test_transacciones_endpoints(self) -> Dict[str, Any]:
        """Probar endpoints de transacciones"""
        results = {}
        headers = self.get_headers()
        today = date.today().isoformat()
        
        tests = [
            ("Transacciones hoy", "GET", f"/api/v1/api/transacciones-flujo-caja/fecha/{today}"),
            ("Dashboard tesorería", "GET", f"/api/v1/api/transacciones-flujo-caja/dashboard/tesoreria/{today}"),
            ("Dashboard pagaduría", "GET", f"/api/v1/api/transacciones-flujo-caja/dashboard/pagaduria/{today}"),
            ("Flujo diario tesorería", "GET", f"/api/v1/api/transacciones-flujo-caja/flujo-diario/{today}/tesoreria"),
            ("Flujo diario pagaduría", "GET", f"/api/v1/api/transacciones-flujo-caja/flujo-diario/{today}/pagaduria"),
        ]
        
        for name, method, endpoint in tests:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                results[name] = {
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "data_count": len(response.json()) if response.status_code == 200 and isinstance(response.json(), list) else None
                }
            except Exception as e:
                results[name] = {"status": "error", "success": False, "error": str(e)}
        
        return results
    
    def test_crud_operations(self) -> Dict[str, Any]:
        """Probar operaciones CRUD básicas"""
        results = {}
        headers = self.get_headers()
        
        # Crear una transacción de prueba
        nueva_transaccion = {
            "concepto_id": 1,  # Asumiendo que existe
            "monto": 100000.0,
            "area": "tesoreria",
            "descripcion": "Transacción de prueba automática",
            "fecha": date.today().isoformat()
        }
        
        try:
            # Crear
            response = requests.post(
                f"{BASE_URL}/api/v1/api/transacciones-flujo-caja/",
                json=nueva_transaccion,
                headers=headers
            )
            
            if response.status_code == 201:
                transaccion_creada = response.json()
                transaccion_id = transaccion_creada.get("id")
                
                results["crear_transaccion"] = {"success": True, "id": transaccion_id}
                
                # Leer
                read_response = requests.get(
                    f"{BASE_URL}/api/v1/api/transacciones-flujo-caja/{transaccion_id}",
                    headers=headers
                )
                results["leer_transaccion"] = {"success": read_response.status_code == 200}
                
                # Actualizar
                update_data = {"monto": 150000.0, "descripcion": "Transacción actualizada"}
                update_response = requests.put(
                    f"{BASE_URL}/api/v1/api/transacciones-flujo-caja/{transaccion_id}",
                    json=update_data,
                    headers=headers
                )
                results["actualizar_transaccion"] = {"success": update_response.status_code == 200}
                
                # Eliminar
                delete_response = requests.delete(
                    f"{BASE_URL}/api/v1/api/transacciones-flujo-caja/{transaccion_id}",
                    headers=headers
                )
                results["eliminar_transaccion"] = {"success": delete_response.status_code == 200}
                
            else:
                results["crear_transaccion"] = {"success": False, "status": response.status_code}
                
        except Exception as e:
            results["crud_error"] = {"success": False, "error": str(e)}
        
        return results

def main():
    print("🚀 VALIDACIÓN COMPLETA DEL SISTEMA DE FLUJO DE CAJA")
    print("=" * 60)
    
    validator = FlujoCajaValidator()
    
    # 1. Probar autenticación con admin
    print("🔐 PROBANDO AUTENTICACIÓN...")
    if validator.login("carlos.gomez@flujo.com", "admin123"):
        print(f"   ✅ Login exitoso como: {validator.user_info.get('nombre')}")
        print(f"   Rol: {validator.user_info.get('rol')}")
    else:
        print("   ❌ Error en autenticación")
        return
    
    # 2. Probar endpoints de conceptos
    print("\n📋 PROBANDO ENDPOINTS DE CONCEPTOS...")
    conceptos_results = validator.test_conceptos_endpoints()
    
    for test_name, result in conceptos_results.items():
        status = "✅" if result["success"] else "❌"
        data_info = f" ({result['data_count']} elementos)" if result.get("data_count") is not None else ""
        print(f"   {status} {test_name}{data_info}")
    
    # 3. Probar endpoints de transacciones
    print("\n💰 PROBANDO ENDPOINTS DE TRANSACCIONES...")
    transacciones_results = validator.test_transacciones_endpoints()
    
    for test_name, result in transacciones_results.items():
        status = "✅" if result["success"] else "❌"
        data_info = f" ({result['data_count']} elementos)" if result.get("data_count") is not None else ""
        print(f"   {status} {test_name}{data_info}")
    
    # 4. Probar operaciones CRUD
    print("\n🔧 PROBANDO OPERACIONES CRUD...")
    crud_results = validator.test_crud_operations()
    
    for operation, result in crud_results.items():
        status = "✅" if result["success"] else "❌"
        print(f"   {status} {operation.replace('_', ' ').title()}")
    
    # 5. Resumen final
    print("\n📊 RESUMEN FINAL:")
    print("-" * 40)
    
    total_tests = 0
    passed_tests = 0
    
    for results in [conceptos_results, transacciones_results, crud_results]:
        for result in results.values():
            total_tests += 1
            if result.get("success"):
                passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"   Total de pruebas: {total_tests}")
    print(f"   Pruebas exitosas: {passed_tests}")
    print(f"   Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("   🎉 Sistema funcionando excelentemente!")
    elif success_rate >= 70:
        print("   ✅ Sistema funcionando bien con pequeños ajustes")
    else:
        print("   ⚠️ Sistema necesita revisión")
    
    print("\n🔗 Para usar la interfaz interactiva:")
    print(f"   👉 http://localhost:8000/docs")

if __name__ == "__main__":
    main()
