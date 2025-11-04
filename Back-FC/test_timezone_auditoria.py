"""
Script para probar que la auditoría registra la hora correcta de Colombia
"""
from datetime import datetime, timezone, timedelta

# Zona horaria de Colombia (UTC-5)
COLOMBIA_TZ = timezone(timedelta(hours=-5))

def obtener_hora_colombia():
    """Obtiene la hora actual en zona horaria de Colombia (UTC-5)"""
    return datetime.now(COLOMBIA_TZ)

print("\n" + "="*80)
print("🕐 VERIFICACIÓN DE ZONA HORARIA")
print("="*80 + "\n")

# Hora UTC
hora_utc = datetime.utcnow()
print(f"⏰ Hora UTC (anterior):        {hora_utc}")
print(f"   Formato ISO: {hora_utc.isoformat()}")

# Hora de Colombia
hora_colombia = obtener_hora_colombia()
print(f"\n⏰ Hora Colombia (nueva):      {hora_colombia}")
print(f"   Formato ISO: {hora_colombia.isoformat()}")

# Diferencia
diferencia = hora_utc.hour - hora_colombia.hour
if diferencia < 0:
    diferencia += 24

print(f"\n📊 Diferencia: {diferencia} horas")
print(f"✅ La hora de Colombia debería ser 5 horas MENOS que UTC")

print("\n" + "="*80)

# Ahora vamos a verificar un registro en la base de datos
print("\n📋 Verificando último registro de auditoría...")
print("="*80 + "\n")

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.auditoria import RegistroAuditoria

db: Session = SessionLocal()
try:
    ultimo_registro = db.query(RegistroAuditoria)\
        .order_by(RegistroAuditoria.fecha_hora.desc())\
        .first()
    
    if ultimo_registro:
        print(f"📝 Último registro de auditoría:")
        print(f"   ID: {ultimo_registro.id}")
        print(f"   Fecha/Hora registrada: {ultimo_registro.fecha_hora}")
        print(f"   Usuario: {ultimo_registro.usuario_nombre}")
        print(f"   Acción: {ultimo_registro.accion}")
        print(f"   Descripción: {ultimo_registro.descripcion}")
        
        # Comparar con hora actual
        hora_actual = obtener_hora_colombia()
        print(f"\n⏰ Hora actual (Colombia): {hora_actual}")
        
        # Calcular diferencia
        if ultimo_registro.fecha_hora.tzinfo is None:
            # Si no tiene zona horaria, asumir que es naive
            diff = datetime.now() - ultimo_registro.fecha_hora
            print(f"⚠️  El registro NO tiene zona horaria (naive datetime)")
        else:
            diff = hora_actual - ultimo_registro.fecha_hora
            print(f"✅ El registro tiene zona horaria")
        
        print(f"📊 Diferencia con ahora: {diff}")
    else:
        print("❌ No hay registros de auditoría")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "="*80)
print("💡 NOTA: Reinicia el servidor backend para que use la nueva zona horaria")
print("="*80 + "\n")
