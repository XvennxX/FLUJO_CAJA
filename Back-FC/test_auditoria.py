from app.core.database import SessionLocal
from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
from app.schemas.flujo_caja import TransaccionFlujoCajaCreate
from datetime import date
import json

db = SessionLocal()
service = TransaccionFlujoCajaService(db)

# Crear una transacción de prueba como usuario ID 6 (Tesorería) con fecha diferente
transaccion_data = TransaccionFlujoCajaCreate(
    fecha=date(2025, 9, 15),  # Fecha diferente
    concepto_id=2,  # CONSUMO
    cuenta_id=1,
    monto=1750.0,
    area='tesoreria',
    descripcion='Prueba de auditoría con usuario tesorería - nueva fecha',
    compania_id=1
)

print('🧪 Creando transacción CONSUMO con usuario ID 6 para 15/09/2025...')
try:
    resultado = service.crear_transaccion(transaccion_data, usuario_id=6)
    print(f'✅ Transacción creada exitosamente: ID {resultado.id}')
    print(f'   Usuario ID: {resultado.usuario_id}')
    print(f'   Concepto ID: {resultado.concepto_id}')
    print(f'   Monto: {resultado.monto}')
    print(f'   Fecha: {resultado.fecha}')
    
    # Verificar si se actualizó automáticamente el SALDO NETO INICIAL PAGADURÍA
    from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
    saldo_neto = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.concepto_id == 4,
        TransaccionFlujoCaja.fecha == date(2025, 9, 15)
    ).order_by(TransaccionFlujoCaja.updated_at.desc()).first()
    
    if saldo_neto:
        print('🤖 SALDO NETO INICIAL PAGADURÍA (debería tener auditoría con usuario 6):')
        print(f'   ID: {saldo_neto.id}')
        print(f'   Usuario ID: {saldo_neto.usuario_id}')
        print(f'   Monto: {saldo_neto.monto}')
        if saldo_neto.auditoria:
            print('   Auditoría existe: SÍ')
            try:
                auditoria = json.loads(saldo_neto.auditoria)
                print(f'   Usuario auditoría: {auditoria.get("usuario_id")}')
                print(f'   Acción: {auditoria.get("accion")}')
                print(f'   Fecha: {auditoria.get("fecha")}')
            except Exception as je:
                print(f'   Error parseando JSON: {je}')
                print(f'   Auditoría raw: {saldo_neto.auditoria[:100]}...')
        else:
            print('   Auditoría: VACÍA')
    else:
        print('🔍 No se encontró SALDO NETO INICIAL PAGADURÍA para esta fecha')

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    print(f'Traceback: {traceback.format_exc()}')
    db.rollback()
finally:
    db.close()
