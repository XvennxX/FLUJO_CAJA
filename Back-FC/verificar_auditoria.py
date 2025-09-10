from app.core.database import SessionLocal
from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
from app.schemas.flujo_caja import TransaccionFlujoCajaCreate
from datetime import date
import json

db = SessionLocal()
service = TransaccionFlujoCajaService(db)

# Verificar la transacción creada automáticamente
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
saldo_neto = db.query(TransaccionFlujoCaja).filter(
    TransaccionFlujoCaja.concepto_id == 4,
    TransaccionFlujoCaja.fecha == date(2025, 9, 15)
).order_by(TransaccionFlujoCaja.updated_at.desc()).first()

if saldo_neto:
    print('🤖 SALDO NETO INICIAL PAGADURÍA auto-generado:')
    print(f'   ID: {saldo_neto.id}')
    print(f'   Usuario ID: {saldo_neto.usuario_id}')
    print(f'   Monto: {saldo_neto.monto}')
    if saldo_neto.auditoria:
        print('   Auditoría existe: SÍ')
        try:
            # Si ya es un diccionario, no necesita parsearse
            if isinstance(saldo_neto.auditoria, dict):
                auditoria = saldo_neto.auditoria
            else:
                auditoria = json.loads(saldo_neto.auditoria)
            
            print(f'   Usuario auditoría: {auditoria.get("usuario_id")}')
            print(f'   Acción: {auditoria.get("accion")}')
            print(f'   Fecha: {auditoria.get("timestamp")}')
            print(f'   Tipo: {auditoria.get("tipo")}')
            print(f'   Concepto: {auditoria.get("concepto_nombre")}')
        except Exception as je:
            print(f'   Error: {je}')
            print(f'   Tipo de auditoría: {type(saldo_neto.auditoria)}')
    else:
        print('   Auditoría: VACÍA')
else:
    print('🔍 No se encontró SALDO NETO INICIAL PAGADURÍA para esta fecha')

db.close()
