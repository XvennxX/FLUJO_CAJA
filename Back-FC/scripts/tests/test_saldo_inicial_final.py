#!/usr/bin/env python3
"""
Script final para probar que el saldo inicial del día 4 se calcule correctamente desde el API.
"""
import requests
import json
from datetime import date

def test_saldo_inicial_via_api():
    """Prueba el cálculo del saldo inicial usando el API"""
    
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 PRUEBA FINAL: Cálculo de saldo inicial via API")
    print("=" * 60)
    
    # Fecha para la cual queremos calcular el saldo inicial (día 4)
    fecha_objetivo = "2025-09-04"
    
    try:
        # Llamar al endpoint de saldo inicial
        url = f"{base_url}/saldo-inicial/calcular-saldo-inicial"
        
        payload = {
            "fecha": fecha_objetivo,
            "area": "TESORERIA"
        }
        
        print(f"📡 Haciendo petición al API...")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"\n📊 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Éxito: {json.dumps(data, indent=2)}")
            
            # Verificar que el resultado tenga el valor esperado ($176.00)
            if 'saldo_inicial_total' in data:
                saldo_calculado = float(data['saldo_inicial_total'])
                valor_esperado = 176.00
                
                print(f"\n🎯 RESULTADO FINAL:")
                print(f"   Fecha objetivo: {fecha_objetivo}")
                print(f"   Saldo inicial calculado: ${saldo_calculado:,.2f}")
                print(f"   Valor esperado: ${valor_esperado:,.2f}")
                
                if abs(saldo_calculado - valor_esperado) < 0.01:  # Permitir pequeñas diferencias de redondeo
                    print(f"   ✅ ÉXITO: El sistema funciona correctamente!")
                    print(f"   ✅ El saldo inicial se calcula desde el SALDO FINAL CUENTAS del día anterior")
                    print(f"   ✅ Valor correcto: ${saldo_calculado:,.2f}")
                else:
                    print(f"   ❌ ERROR: El valor no coincide")
                    print(f"   ❌ Se esperaba ${valor_esperado:,.2f} pero se obtuvo ${saldo_calculado:,.2f}")
            else:
                print("   ❌ ERROR: La respuesta no contiene 'saldo_inicial_total'")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")
        print("   ¿Está el servidor ejecutándose en http://localhost:8000?")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_saldo_inicial_via_api()
