import sys
sys.path.append('c:/Users/1006509625/Desktop/PROYECTO/Back-FC')

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from datetime import date

db = next(get_db())
fecha_prueba = date(2024, 9, 3)

print(f'🧮 Verificando transacciones para {fecha_prueba}...')

# Verificar transacciones para SALDO NETO INICIAL PAGADURÍA (ID: 4)
trans_saldo_neto = db.query(TransaccionFlujoCaja).filter(
    TransaccionFlujoCaja.fecha == fecha_prueba,
    TransaccionFlujoCaja.concepto_id == 4
).first()

# Verificar transacciones para SUB-TOTAL TESORERÍA (ID: 50)
trans_sub_total = db.query(TransaccionFlujoCaja).filter(
    TransaccionFlujoCaja.fecha == fecha_prueba,
    TransaccionFlujoCaja.concepto_id == 50
).first()

print('💰 SALDO NETO INICIAL PAGADURÍA:', trans_saldo_neto.monto if trans_saldo_neto else 'No encontrada')
print('💰 SUB-TOTAL TESORERÍA:', trans_sub_total.monto if trans_sub_total else 'No encontrada')

if trans_saldo_neto and trans_sub_total:
    suma_esperada = trans_saldo_neto.monto + trans_sub_total.monto
    print(f'📈 Suma esperada SALDO FINAL CUENTAS: {suma_esperada}')
else:
    print('⚠️ Faltan transacciones base para el cálculo')
    
    # Listar todas las transacciones de esa fecha
    todas_trans = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_prueba
    ).all()
    
    print(f'📋 Total transacciones en {fecha_prueba}: {len(todas_trans)}')
    for trans in todas_trans:
        concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == trans.concepto_id).first()
        nombre_concepto = concepto.nombre if concepto else f'ID: {trans.concepto_id}'
        print(f'  - {nombre_concepto}: {trans.monto}')
