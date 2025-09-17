#!/usr/bin/env python3
"""
Script para arreglar el archivo API que tiene métodos duplicados
"""

import re

# Leer el archivo corrupto
with open('app/api/transacciones_flujo_caja.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("🔍 Archivo original tiene", len(content.splitlines()), "líneas")

# Buscar y eliminar el primer método recalcular_dependencias_fecha corrupto
# que tiene el contenido del método duplicado PUT
pattern1 = r'# MÉTODO DUPLICADO ELIMINADO[^@]*@router\.post\("/recalcular-dependencias/\{fecha\}".*?\n.*?def recalcular_dependencias_fecha\(.*?\n.*?"Actualizar una transacción existente con recálculo automático de dependencias".*?raise HTTPException\(status_code=status\.HTTP_500_INTERNAL_SERVER_ERROR.*?\n\n@router\.post\("/recalcular-dependencias/\{fecha\}"'

# Reemplazarlo con solo el comentario y el inicio del método bueno
replacement1 = '# MÉTODO DUPLICADO ELIMINADO - Solo mantenemos el primer método PUT con auto-cálculo\n\n@router.post("/recalcular-dependencias/{fecha}"'

# Aplicar la limpieza
content_clean = re.sub(pattern1, replacement1, content, flags=re.DOTALL)

print("🧹 Después de limpeza tiene", len(content_clean.splitlines()), "líneas")

# Guardar el archivo arreglado
with open('app/api/transacciones_flujo_caja.py', 'w', encoding='utf-8') as f:
    f.write(content_clean)

print("✅ Archivo arreglado exitosamente!")
print("📂 Backup disponible en: transacciones_flujo_caja_backup.py")