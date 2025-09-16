from app.core.database import SessionLocal
from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
from app.schemas.flujo_caja import TransaccionFlujoCajaCreate
from datetime import date
import json

db = SessionLocal()
service = TransaccionFlujoCajaService(db)

# Crear una transacción de PAGOS INTERCOMPAÑÍAS (ID 5) para probar SUB TOTAL
transaccion_data = TransaccionFlujoCajaCreate(
    fecha=date(2025, 9, 16),  # Nueva fecha
    concepto_id=5,  # PAGOS INTERCOMPAÑÍAS (renta fija)
    cuenta_id=1,
    monto=200.0,
    area='tesoreria',
    descripcion='Prueba SUB TOTAL TESORERÍA - PAGOS INTERCOMPAÑÍAS',
    compania_id=1
)

print('🧪 Creando transacción PAGOS INTERCOMPAÑÍAS (ID 5) para probar SUB TOTAL...')
try:
    resultado = service.crear_transaccion(transaccion_data, usuario_id=6)
    print(f'✅ Transacción creada exitosamente: ID {resultado.id}')
    print(f'   Usuario ID: {resultado.usuario_id}')
    print(f'   Concepto ID: {resultado.concepto_id}')
    print(f'   Monto: {resultado.monto}')
    print(f'   Fecha: {resultado.fecha}')
    
    # Verificar si se creó/actualizó automáticamente el SUB TOTAL TESORERÍA
    from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
    subtotal = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.concepto_id == 50,
        TransaccionFlujoCaja.fecha == date(2025, 9, 16)
    ).order_by(TransaccionFlujoCaja.updated_at.desc()).first()
    
    if subtotal:
        print(f'🤖 SUB TOTAL TESORERÍA auto-generado:')
        print(f'   ID: {subtotal.id}')
        print(f'   Usuario ID: {subtotal.usuario_id}')
        print(f'   Monto: {subtotal.monto}')
        if subtotal.auditoria:
            print('   Auditoría existe: SÍ')
            try:
                # Si ya es un diccionario, no necesita parsearse
                if isinstance(subtotal.auditoria, dict):
                    auditoria = subtotal.auditoria
                else:
                    auditoria = json.loads(subtotal.auditoria)
                
                print(f'   Usuario auditoría: {auditoria.get("usuario_id")}')
                print(f'   Acción: {auditoria.get("accion")}')
                print(f'   Tipo: {auditoria.get("tipo")}')
                print(f'   Concepto: {auditoria.get("concepto_nombre")}')
            except Exception as je:
                print(f'   Error parseando auditoría: {je}')
        else:
            print('   Auditoría: VACÍA')
    else:
        print('🔍 No se encontró SUB TOTAL TESORERÍA para esta fecha')
        
    # También verificar SALDO FINAL CUENTAS (que depende del SUB TOTAL)
    saldo_final = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.concepto_id == 51,
        TransaccionFlujoCaja.fecha == date(2025, 9, 16)
    ).order_by(TransaccionFlujoCaja.updated_at.desc()).first()
    
    if saldo_final:
        print(f'🏁 SALDO FINAL CUENTAS también se actualizó:')
        print(f'   ID: {saldo_final.id}')
        print(f'   Monto: {saldo_final.monto}')

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    print(f'Traceback: {traceback.format_exc()}')
    db.rollback()
finally:
    db.close()
