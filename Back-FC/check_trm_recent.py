from app.core.database import SessionLocal
from app.models.trm import TRM
from datetime import date, timedelta

db = SessionLocal()
hoy = date.today()

print('\nTRMs de los últimos 11 días:')
print('='*50)

for i in range(10, -1, -1):
    fecha = hoy - timedelta(days=i)
    dia_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'][fecha.weekday()]
    trm = db.query(TRM).filter(TRM.fecha == fecha).first()
    
    if trm:
        print(f'{fecha} ({dia_semana}): ${trm.valor:,.2f}')
    else:
        print(f'{fecha} ({dia_semana}): ❌ FALTA')

db.close()
