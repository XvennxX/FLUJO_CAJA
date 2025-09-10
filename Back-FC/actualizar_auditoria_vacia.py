#!/usr/bin/env python3
"""
Script para actualizar transacciones con auditoría vacía
Agrega información de auditoría a transacciones creadas automáticamente
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from datetime import datetime, date
from app.core.database import SessionLocal
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja

def actualizar_auditoria_vacia():
    """Actualiza transacciones con auditoría vacía"""
    
    db = SessionLocal()
    try:
        print("🔍 Buscando transacciones con auditoría vacía...")
        
        # Buscar transacciones sin auditoría o con auditoría None
        transacciones_sin_auditoria = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.auditoria.is_(None)
        ).all()
        
        print(f"📊 Encontradas {len(transacciones_sin_auditoria)} transacciones sin auditoría")
        
        for trans in transacciones_sin_auditoria:
            # Obtener información del concepto
            concepto = db.query(ConceptoFlujoCaja).filter(
                ConceptoFlujoCaja.id == trans.concepto_id
            ).first()
            
            # Determinar si es una transacción automática o manual
            es_automatica = (
                trans.descripcion and 
                "automáticamente" in trans.descripcion.lower()
            )
            
            # Crear auditoría apropiada
            if es_automatica:
                auditoria = {
                    "accion": "creacion_automatica",
                    "usuario_id": trans.usuario_id or 1,
                    "timestamp": trans.created_at.isoformat() if trans.created_at else datetime.now().isoformat(),
                    "monto_inicial": float(trans.monto),
                    "formula": concepto.formula_dependencia if concepto else None,
                    "tipo": "dependencia_automatica",
                    "concepto_nombre": concepto.nombre if concepto else "Desconocido",
                    "actualizado_por_script": True,
                    "fecha_actualizacion": datetime.now().isoformat()
                }
            else:
                auditoria = {
                    "accion": "creacion_manual",
                    "usuario_id": trans.usuario_id or 1,
                    "timestamp": trans.created_at.isoformat() if trans.created_at else datetime.now().isoformat(),
                    "monto_inicial": float(trans.monto),
                    "tipo": "ingreso_manual",
                    "concepto_nombre": concepto.nombre if concepto else "Desconocido",
                    "actualizado_por_script": True,
                    "fecha_actualizacion": datetime.now().isoformat()
                }
            
            # Actualizar la transacción
            trans.auditoria = auditoria
            
            print(f"✅ Actualizada transacción ID {trans.id}:")
            print(f"   📋 Concepto: {concepto.nombre if concepto else 'Desconocido'}")
            print(f"   💰 Monto: ${trans.monto}")
            print(f"   🤖 Tipo: {'Automática' if es_automatica else 'Manual'}")
            print(f"   📅 Fecha: {trans.fecha}")
            print()
        
        # Confirmar cambios
        db.commit()
        
        print(f"🎯 COMPLETADO: Actualizadas {len(transacciones_sin_auditoria)} transacciones")
        print("✅ Todas las transacciones ahora tienen información de auditoría completa")
        
    except Exception as e:
        print(f"❌ Error durante la actualización: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    actualizar_auditoria_vacia()
