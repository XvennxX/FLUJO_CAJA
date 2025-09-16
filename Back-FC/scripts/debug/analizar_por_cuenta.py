from app.core.database import SessionLocal
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.cuentas_bancarias import CuentaBancaria
from datetime import date

db = SessionLocal()

# Ver todas las cuentas bancarias
print('🏦 Cuentas bancarias disponibles:')
cuentas = db.query(CuentaBancaria).all()
for cuenta in cuentas:
    banco_nombre = cuenta.banco.nombre if cuenta.banco else "Sin banco"
    print(f'   ID {cuenta.id}: {cuenta.numero_cuenta} - {banco_nombre}')

print('\n📊 SUB TOTAL TESORERÍA por cuenta para 09/09/2025:')
for cuenta in cuentas:
    subtotal = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.concepto_id == 50,
        TransaccionFlujoCaja.fecha == date(2025, 9, 9),
        TransaccionFlujoCaja.cuenta_id == cuenta.id
    ).first()
    
    if subtotal:
        print(f'   Cuenta {cuenta.numero_cuenta}: ${subtotal.monto}')
    else:
        print(f'   Cuenta {cuenta.numero_cuenta}: No calculado')

print('\n🔍 Transacciones de tesorería (conceptos 5-49) por cuenta:')
for cuenta in cuentas:
    transacciones = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == date(2025, 9, 9),
        TransaccionFlujoCaja.concepto_id >= 5,
        TransaccionFlujoCaja.concepto_id <= 49,
        TransaccionFlujoCaja.cuenta_id == cuenta.id
    ).all()
    
    if transacciones:
        total = sum(float(t.monto) for t in transacciones)
        print(f'   Cuenta {cuenta.numero_cuenta}: {len(transacciones)} transacciones, total ${total}')
    else:
        print(f'   Cuenta {cuenta.numero_cuenta}: Sin transacciones de tesorería')

db.close()
