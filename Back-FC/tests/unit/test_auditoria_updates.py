"""
Script para verificar que la auditoría registra correctamente las actualizaciones
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.auditoria import RegistroAuditoria
from datetime import datetime, timedelta

def verificar_auditoria():
    """Verificar los últimos registros de auditoría"""
    db: Session = SessionLocal()
    try:
        print("\n" + "="*80)
        print("📊 VERIFICACIÓN DE AUDITORÍA - ÚLTIMOS 10 REGISTROS")
        print("="*80 + "\n")
        
        # Obtener los últimos 10 registros de auditoría
        registros = db.query(RegistroAuditoria)\
            .order_by(RegistroAuditoria.fecha_hora.desc())\
            .limit(10)\
            .all()
        
        if not registros:
            print("❌ No se encontraron registros de auditoría")
            return
        
        print(f"✅ Se encontraron {len(registros)} registros de auditoría\n")
        
        for i, registro in enumerate(registros, 1):
            print(f"{i}. {'='*75}")
            print(f"   🕐 Fecha/Hora: {registro.fecha_hora}")
            print(f"   👤 Usuario ID: {registro.usuario_id}")
            print(f"   🎯 Acción: {registro.accion}")
            print(f"   📦 Módulo: {registro.modulo}")
            print(f"   📝 Descripción: {registro.descripcion}")
            print(f"   🌐 IP: {registro.ip_address}")
            if hasattr(registro, 'valores_anteriores') and registro.valores_anteriores:
                print(f"   � Valores anteriores: {registro.valores_anteriores}")
            if hasattr(registro, 'valores_nuevos') and registro.valores_nuevos:
                print(f"   📊 Valores nuevos: {registro.valores_nuevos}")
            print()
        
        # Estadísticas por acción
        print("\n" + "="*80)
        print("📈 ESTADÍSTICAS POR TIPO DE ACCIÓN")
        print("="*80 + "\n")
        
        from sqlalchemy import func
        stats = db.query(
            RegistroAuditoria.accion,
            func.count(RegistroAuditoria.id).label('total')
        ).group_by(RegistroAuditoria.accion).all()
        
        for accion, total in stats:
            print(f"   {accion}: {total} registros")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"❌ Error al verificar auditoría: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verificar_auditoria()
