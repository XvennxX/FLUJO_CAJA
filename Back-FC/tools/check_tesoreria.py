from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Registros de TESORERÍA
    result = conn.execute(text('''
        SELECT id, fecha, concepto_id, cuenta_id, area, monto 
        FROM transacciones_flujo_caja 
        WHERE area = 'tesoreria'
        ORDER BY id DESC 
        LIMIT 20
    '''))
    
    print('ÚLTIMOS 20 REGISTROS DE TESORERÍA:')
    print('-' * 80)
    for r in result.fetchall():
        print(f'ID: {r[0]} | Fecha: {r[1]} | Concepto: {r[2]} | Cuenta: {r[3]} | Área: {r[4]} | Monto: {r[5]}')
    
    # Registros de PAGADURÍA  
    result2 = conn.execute(text('''
        SELECT id, fecha, concepto_id, cuenta_id, area, monto 
        FROM transacciones_flujo_caja 
        WHERE area = 'pagaduria'
        ORDER BY id DESC 
        LIMIT 20
    '''))
    
    print('\n\nÚLTIMOS 20 REGISTROS DE PAGADURÍA:')
    print('-' * 80)
    for r in result2.fetchall():
        print(f'ID: {r[0]} | Fecha: {r[1]} | Concepto: {r[2]} | Cuenta: {r[3]} | Área: {r[4]} | Monto: {r[5]}')
