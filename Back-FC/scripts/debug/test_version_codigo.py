#!/usr/bin/env python3
"""
Test para verificar que se está usando la versión correcta del código
"""

import sys
import os
import inspect

# Configurar el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

def test_version_codigo():
    """Verificar que se está usando la versión correcta del código"""
    print("🔍 === VERIFICACIÓN DE VERSIÓN DEL CÓDIGO === 🔍")
    
    try:
        from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
        
        print(f"\n1. 📁 Archivo importado desde:")
        print(f"   {inspect.getfile(TransaccionFlujoCajaService)}")
        
        print(f"\n2. 🔍 Inspeccionando método actualizar_transaccion:")
        
        # Obtener el código fuente del método
        metodo = getattr(TransaccionFlujoCajaService, 'actualizar_transaccion')
        codigo_fuente = inspect.getsource(metodo)
        
        # Buscar nuestros prints de debug
        if "DEBUG actualizar_transaccion:" in codigo_fuente:
            print(f"   ✅ Los prints de debug SÍ están en el código")
        else:
            print(f"   ❌ Los prints de debug NO están en el código")
            
        if "procesar_dependencias_completas_ambos_dashboards" in codigo_fuente:
            print(f"   ✅ El método de auto-cálculo SÍ está en el código")
        else:
            print(f"   ❌ El método de auto-cálculo NO está en el código")
            
        # Mostrar las líneas relevantes
        lineas = codigo_fuente.split('\n')
        print(f"\n3. 📄 Líneas del método que contienen 'update_data' o 'DEBUG':")
        for i, linea in enumerate(lineas):
            if 'update_data' in linea or 'DEBUG' in linea or 'procesar_dependencias' in linea:
                print(f"   {i+1:3}: {linea.strip()}")
                
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_version_codigo()