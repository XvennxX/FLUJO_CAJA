from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT id, nombre, area 
        FROM conceptos_flujo_caja 
        WHERE nombre IN ('SALDO INICIAL', 'SALDO DIA ANTERIOR')
    '''))
    
    print('CONCEPTOS ENCONTRADOS:')
    print('-' * 60)
    for r in result.fetchall():
        print(f'ID: {r[0]} | Nombre: {r[1]} | Área: {r[2]}')
