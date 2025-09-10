import sys
sys.path.append('c:/Users/1006509625/Desktop/PROYECTO/Back-FC')

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from app.schemas.flujo_caja import TransaccionFlujoCajaCreate
from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
from datetime import date

db = next(get_db())
service = TransaccionFlujoCajaService(db)
fecha_dia_3 = date(2024, 9, 3)

print(f'💾 Creando transacciones para {fecha_dia_3}...')

# Basándome en las capturas de pantalla del usuario, el día 3 mostraba:
# SALDO FINAL CUENTAS: $60

# Para que SALDO FINAL CUENTAS = SALDO NETO INICIAL PAGADURÍA + SUB-TOTAL TESORERÍA = $60
# Vamos a crear transacciones que sumen eso

transacciones_dia_3 = [
    # SALDO NETO INICIAL PAGADURÍA = $30 (ejemplo)
    {
        'concepto_id': 4,  # SALDO NETO INICIAL PAGADURÍA
        'monto': 30.0,
        'descripcion': 'Saldo neto inicial día 3'
    },
    # SUB-TOTAL TESORERÍA = $30 (para que sumen $60)
    {
        'concepto_id': 50,  # SUB-TOTAL TESORERÍA
        'monto': 30.0,
        'descripcion': 'Sub-total tesorería día 3'
    }
]

try:
    for transaccion_data in transacciones_dia_3:
        # Verificar si ya existe
        existe = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_dia_3,
            TransaccionFlujoCaja.concepto_id == transaccion_data['concepto_id']
        ).first()
        
        if not existe:
            # Crear la transacción
            nueva_transaccion = TransaccionFlujoCajaCreate(
                fecha=fecha_dia_3,
                concepto_id=transaccion_data['concepto_id'],
                cuenta_id=None,
                monto=transaccion_data['monto'],
                descripcion=transaccion_data['descripcion'],
                area='TESORERIA',
                compania_id=1
            )
            
            resultado = service.crear_transaccion(nueva_transaccion, usuario_id=1)
            concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == transaccion_data['concepto_id']).first()
            print(f'✅ Creada: {concepto.nombre} = ${transaccion_data["monto"]}')
        else:
            concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == transaccion_data['concepto_id']).first()
            print(f'⚠️ Ya existe: {concepto.nombre} = ${existe.monto}')
    
    print('\n🔄 Procesando dependencias automáticas...')
    
    # Ahora verificar si se creó automáticamente SALDO FINAL CUENTAS
    saldo_final_trans = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_dia_3,
        TransaccionFlujoCaja.concepto_id == 51  # SALDO FINAL CUENTAS
    ).first()
    
    if saldo_final_trans:
        print(f'🎉 SALDO FINAL CUENTAS creado automáticamente: ${saldo_final_trans.monto}')
    else:
        print('❌ SALDO FINAL CUENTAS no se creó automáticamente')
        
        # Forzar el procesamiento manual
        from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
        dep_service = DependenciasFlujoCajaService(db)
        dep_service.procesar_dependencias_avanzadas(
            fecha=fecha_dia_3,
            area='TESORERIA',
            concepto_modificado_id=None,
            cuenta_id=None,
            compania_id=1
        )
        
        # Verificar de nuevo
        saldo_final_trans = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_dia_3,
            TransaccionFlujoCaja.concepto_id == 51
        ).first()
        
        if saldo_final_trans:
            print(f'🎉 SALDO FINAL CUENTAS creado manualmente: ${saldo_final_trans.monto}')
        else:
            print('❌ SALDO FINAL CUENTAS aún no se pudo crear')

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
