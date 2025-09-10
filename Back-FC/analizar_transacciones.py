from app.core.database import SessionLocal
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from datetime import date

db = SessionLocal()

# Ver todas las transacciones del 09/09/2025
print('📊 Transacciones del 09/09/2025:')
transacciones = db.query(TransaccionFlujoCaja).filter(
    TransaccionFlujoCaja.fecha == date(2025, 9, 9)
).order_by(TransaccionFlujoCaja.concepto_id).all()

total_tesoreria_manual = 0
for t in transacciones:
    print(f'   ID {t.id}: Concepto {t.concepto_id} = ${t.monto}')
    # Sumar solo conceptos de tesorería (5-49)
    if 5 <= t.concepto_id <= 49:
        total_tesoreria_manual += float(t.monto)

print(f'\n📐 Suma manual de conceptos 5-49: ${total_tesoreria_manual}')

# Ver qué muestra el SUB TOTAL TESORERÍA
subtotal = db.query(TransaccionFlujoCaja).filter(
    TransaccionFlujoCaja.concepto_id == 50,
    TransaccionFlujoCaja.fecha == date(2025, 9, 9)
).first()

if subtotal:
    print(f'🏷️ SUB TOTAL TESORERÍA guardado: ${subtotal.monto}')
    coincide = float(subtotal.monto) == total_tesoreria_manual
    print(f'   ¿Coincide? {"✅ SÍ" if coincide else "❌ NO"}')
else:
    print('❌ No se encontró SUB TOTAL TESORERÍA para el 09/09/2025')

db.close()
