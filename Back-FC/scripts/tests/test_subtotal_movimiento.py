#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para SUBTOTAL MOVIMIENTO PAGADURIA = SUMA de conceptos 55-81
Respetando códigos: I(Ingreso +), E(Egreso -), N(Neutral +)
"""

import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from decimal import Decimal
from sqlalchemy import text

def main():
    print("=== TEST SUBTOTAL MOVIMIENTO PAGADURIA (Con códigos I/E/N) ===")
    print("🎯 Probando: SUBTOTAL = Ingresos(+) + Egresos(-) + Neutrales(+)")
    
    db = SessionLocal()
    try:
        fecha_test = datetime(2025, 9, 10).date()
        print(f"📅 Fecha de prueba: {fecha_test}")
        
        # 1. Verificar códigos de algunos conceptos en la BD
        print("\n1. Verificando códigos de conceptos en la BD...")
        conceptos_muestra = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.id.between(55, 65)
        ).all()
        
        for concepto in conceptos_muestra:
            codigo_desc = {"I": "Ingreso(+)", "E": "Egreso(-)", "N": "Neutral(+)", None: "Sin código"}
            print(f"   • [{concepto.id}] {concepto.nombre}: {concepto.codigo} ({codigo_desc.get(concepto.codigo, '?')})")
        
        # 2. Limpiar datos anteriores
        print("\n2. Limpiando datos anteriores...")
        db.execute(text("""
            DELETE FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id IN (55, 56, 57, 82)
            AND area = 'pagaduria'
            AND cuenta_id = 1
        """), {"fecha": fecha_test})
        db.commit()
        
        # 3. Crear transacciones de ejemplo con diferentes códigos
        print("\n3. Creando transacciones de ejemplo...")
        
        # Buscar conceptos reales con sus códigos
        conceptos_test = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.id.in_([55, 56, 57, 70, 75])
        ).all()
        
        transacciones_ejemplo = [
            {"concepto_id": 55, "monto": Decimal('1000.00')},  # Debería ser según su código en BD
            {"concepto_id": 56, "monto": Decimal('500.00')},   # Debería ser según su código en BD
            {"concepto_id": 57, "monto": Decimal('300.00')},   # Debería ser según su código en BD
            {"concepto_id": 70, "monto": Decimal('200.00')},   # Debería ser según su código en BD
            {"concepto_id": 75, "monto": Decimal('800.00')},   # Debería ser según su código en BD
        ]
        
        total_esperado_manual = Decimal('0.00')
        conceptos_detalle = []
        
        for trans in transacciones_ejemplo:
            # Buscar el concepto para obtener su código
            concepto = next((c for c in conceptos_test if c.id == trans["concepto_id"]), None)
            if concepto:
                # Crear transacción
                transaccion = TransaccionFlujoCaja(
                    fecha=fecha_test,
                    concepto_id=trans["concepto_id"],
                    cuenta_id=1,
                    monto=trans["monto"],
                    descripcion=f"Test - {concepto.nombre}",
                    usuario_id=6,
                    area=AreaTransaccion.pagaduria,
                    compania_id=1,
                    auditoria={"test": "subtotal_movimiento"}
                )
                
                db.add(transaccion)
                
                # Calcular cómo debe afectar al subtotal según el código
                if concepto.codigo == 'E':  # Egreso - negativo
                    efecto = -abs(trans["monto"])
                    signo = "(-)"
                elif concepto.codigo == 'I':  # Ingreso - positivo
                    efecto = abs(trans["monto"])
                    signo = "(+)"
                elif concepto.codigo == 'N':  # Neutral - positivo
                    efecto = abs(trans["monto"])
                    signo = "(+)"
                else:  # Sin código - mantener original
                    efecto = trans["monto"]
                    signo = "(?)"
                
                total_esperado_manual += efecto
                conceptos_detalle.append({
                    "id": concepto.id,
                    "nombre": concepto.nombre,
                    "codigo": concepto.codigo,
                    "monto": trans["monto"],
                    "efecto": efecto,
                    "signo": signo
                })
                
                print(f"   • [{concepto.id}] {concepto.nombre} ({concepto.codigo}): ${trans['monto']} → {signo}${abs(efecto)}")
        
        db.commit()
        print(f"   💰 Total esperado: ${total_esperado_manual}")
        
        # 4. Verificar estado ANTES del procesamiento
        print("\n4. Estado ANTES del procesamiento...")
        subtotal_antes = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 82
            AND area = 'pagaduria'
            AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        count_antes, monto_antes = subtotal_antes
        print(f"   SUBTOTAL MOVIMIENTO antes: {count_antes} registros, Total: ${monto_antes}")
        
        # 5. Ejecutar procesamiento
        print("\n5. Ejecutando procesamiento de dependencias...")
        service = DependenciasFlujoCajaService(db)
        actualizaciones = service._procesar_dependencias_pagaduria(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📝 Actualizaciones realizadas: {len(actualizaciones)}")
        
        # 6. Verificar resultado
        print("\n6. Verificando resultado...")
        subtotal_despues = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 82
            AND area = 'pagaduria'
            AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        count_despues, monto_despues = subtotal_despues
        print(f"   SUBTOTAL MOVIMIENTO después: {count_despues} registros, Total: ${monto_despues}")
        
        # 7. Validar resultado
        if count_despues > count_antes:
            print(f"\n� Análisis de resultado:")
            print(f"   💰 Resultado obtenido: ${monto_despues}")
            print(f"   💰 Esperado (manual): ${total_esperado_manual}")
            print(f"   ✅ Coinciden: {'SÍ' if monto_despues == total_esperado_manual else 'NO'}")
            
            if monto_despues == total_esperado_manual:
                print(f"\n🎉 ¡ÉXITO! SUBTOTAL MOVIMIENTO calculado correctamente con códigos I/E/N")
            else:
                print(f"\n⚠️ Diferencia detectada - verificar lógica")
                
        else:
            print(f"\n❌ ERROR: No se creó el SUBTOTAL MOVIMIENTO")
        
        # 8. Mostrar detalles de la actualización
        print(f"\n📊 Detalles de actualizaciones:")
        for update in actualizaciones:
            concepto_id = update.get('concepto_id')
            concepto_nombre = update.get('concepto_nombre', 'N/A')
            monto_nuevo = update.get('monto_nuevo', 0)
            print(f"\n   • [{concepto_id}] {concepto_nombre}: ${monto_nuevo}")
            
            # Mostrar detalles específicos del SUBTOTAL MOVIMIENTO
            if concepto_id == 82:
                conceptos_incluidos = update.get('conceptos_incluidos', [])
                formula = update.get('formula_aplicada', 'N/A')
                print(f"     ↳ Fórmula: {formula}")
                print(f"     ↳ Incluye {len(conceptos_incluidos)} conceptos:")
                for concepto in conceptos_incluidos:
                    nombre = concepto.get('concepto_nombre', f"ID {concepto['concepto_id']}")
                    codigo = concepto.get('codigo', '?')
                    monto_orig = concepto.get('monto_original', 0)
                    monto_calc = concepto.get('monto_calculado', 0)
                    signo = concepto.get('signo', '?')
                    print(f"       - {nombre} ({codigo}): ${monto_orig} → ${monto_calc} {signo}")
        
        # 9. Resumen final
        print(f"\n📋 Resumen del cálculo:")
        for detalle in conceptos_detalle:
            print(f"   {detalle['nombre']} ({detalle['codigo']}): ${detalle['monto']} → {detalle['signo']}${abs(detalle['efecto'])}")
        print(f"   ──────────────────────────")
        print(f"   TOTAL: ${total_esperado_manual}")
        print(f"   RESULTADO: ${monto_despues}")
        print(f"   CORRECTO: {'✅ SÍ' if monto_despues == total_esperado_manual else '❌ NO'}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
