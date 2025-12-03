from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Eliminar transacciones importadas de septiembre
    result = conn.execute(text('''
        DELETE FROM transacciones_flujo_caja 
        WHERE descripcion LIKE '%Importación Excel%'
        AND fecha >= '2025-09-01'
        AND fecha < '2025-10-01'
    '''))
    
    conn.commit()
    
    print(f'✓ Eliminadas {result.rowcount} transacciones de importación de septiembre')
    print('Ahora puedes volver a importar el Excel con el código actualizado')
