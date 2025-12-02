from app.core.database import SessionLocal
from app.models.dias_festivos import DiaFestivo
from datetime import date

db = SessionLocal()

print('\nFestivos de noviembre 2025:')
print('='*50)

festivos = db.query(DiaFestivo).filter(
    DiaFestivo.fecha >= date(2025, 11, 1),
    DiaFestivo.fecha <= date(2025, 11, 30),
    DiaFestivo.activo == True
).order_by(DiaFestivo.fecha).all()

if festivos:
    for f in festivos:
        print(f'{f.fecha}: {f.nombre} ({f.tipo})')
else:
    print('❌ NO HAY FESTIVOS CARGADOS EN LA TABLA')

db.close()
