from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT id, fecha, concepto_id, cuenta_id, area, monto, descripcion 
        FROM transacciones_flujo_caja 
        ORDER BY id DESC 
        LIMIT 30
    '''))
    rows = result.fetchall()
    
    print('ID | Fecha | Concepto | Cuenta | Area | Monto | Descripcion')
    print('-' * 100)
    for r in rows:
        print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]}')
    
    # Contar por área
    result2 = conn.execute(text('SELECT area, COUNT(*) as total FROM transacciones_flujo_caja GROUP BY area'))
    print('\n\nCONTEO POR ÁREA:')
    print('-' * 40)
    for r in result2.fetchall():
        print(f'{r[0]}: {r[1]} registros')
