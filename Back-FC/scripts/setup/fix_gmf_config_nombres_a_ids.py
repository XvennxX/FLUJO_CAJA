"""
Script para corregir configuraciones GMF que tienen nombres en lugar de IDs.
Convierte los nombres de conceptos a sus IDs correspondientes.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.database import SessionLocal
from app.models.gmf_config import GMFConfig
from app.models import ConceptoFlujoCaja
import json

def fix_gmf_configs():
    db = SessionLocal()
    try:
        print("🔧 Corrigiendo configuraciones GMF...")
        
        # Obtener todas las configuraciones activas
        configs = db.query(GMFConfig).filter(GMFConfig.activo == True).all()
        print(f"📊 Encontradas {len(configs)} configuraciones activas")
        
        # Obtener todos los conceptos para mapeo
        conceptos = db.query(ConceptoFlujoCaja).all()
        nombre_a_id = {c.nombre: c.id for c in conceptos}
        
        configs_corregidos = 0
        configs_ya_correctos = 0
        
        for config in configs:
            if not config.conceptos_seleccionados:
                continue
                
            try:
                data = json.loads(config.conceptos_seleccionados)
                
                # Verificar si son nombres (strings) o IDs (números)
                if data and isinstance(data[0], str):
                    print(f"\n🔄 Corrigiendo config ID {config.id} (Cuenta {config.cuenta_bancaria_id})")
                    print(f"   Antes: {data[:3]}...")
                    
                    # Convertir nombres a IDs
                    ids = []
                    for item in data:
                        if isinstance(item, str):
                            if item in nombre_a_id:
                                ids.append(nombre_a_id[item])
                                print(f"   ✅ '{item}' → ID {nombre_a_id[item]}")
                            else:
                                print(f"   ⚠️ Concepto '{item}' no encontrado")
                        elif isinstance(item, dict) and 'id' in item:
                            ids.append(int(item['id']))
                        elif isinstance(item, (int, float)):
                            ids.append(int(item))
                    
                    # Guardar IDs corregidos
                    config.conceptos_seleccionados = json.dumps(ids)
                    configs_corregidos += 1
                    print(f"   Después: {ids[:5]}...")
                    
                elif data and isinstance(data[0], (int, float)):
                    configs_ya_correctos += 1
                    print(f"✅ Config ID {config.id} ya tiene IDs numéricos")
                    
                elif data and isinstance(data[0], dict) and 'id' in data[0]:
                    # Convertir de [{id: 1}, {id: 2}] a [1, 2]
                    ids = [int(item['id']) for item in data]
                    config.conceptos_seleccionados = json.dumps(ids)
                    configs_corregidos += 1
                    print(f"✅ Config ID {config.id} convertido de formato dict a IDs simples")
                    
            except Exception as e:
                print(f"❌ Error procesando config ID {config.id}: {e}")
                continue
        
        # Confirmar cambios
        db.commit()
        
        print(f"\n📊 Resumen:")
        print(f"   ✅ Configuraciones corregidas: {configs_corregidos}")
        print(f"   ✓ Configuraciones ya correctas: {configs_ya_correctos}")
        print(f"   📝 Total procesadas: {len(configs)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_gmf_configs()
