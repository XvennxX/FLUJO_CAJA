#!/usr/bin/env python3
"""
Script para verificar la estructura y organización del proyecto.
Verifica que los archivos estén en las ubicaciones correctas y
detecta posibles problemas organizacionales.
"""

import os
import glob
from pathlib import Path

def check_project_structure():
    """Verificar la estructura del proyecto"""
    print("🔍 Verificando estructura del proyecto...\n")
    
    # Directorio base del proyecto
    project_root = Path(__file__).parent.parent
    
    # Verificaciones
    issues = []
    warnings = []
    
    # 1. Verificar que existan las carpetas principales
    required_dirs = [
        "Back-FC/app",
        "Back-FC/tests", 
        "Back-FC/scripts",
        "Back-FC/docs",
        "Front-FC/src",
        "tools/debug",
        "tools/setup", 
        "tools/maintenance",
        "docs"
    ]
    
    print("📁 Verificando directorios requeridos:")
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            issues.append(f"❌ Directorio faltante: {dir_path}")
            print(f"  ❌ {dir_path}")
    
    # 2. Buscar archivos en ubicaciones incorrectas
    print("\n🔍 Buscando archivos mal ubicados:")
    
    # Scripts de test en lugares incorrectos
    test_files_root = list(project_root.glob("test_*.py"))
    if test_files_root:
        warnings.append(f"⚠️  Scripts de test en directorio raíz: {[f.name for f in test_files_root]}")
    
    # Scripts de debug en lugares incorrectos  
    debug_files_root = list(project_root.glob("debug_*.py"))
    if debug_files_root:
        warnings.append(f"⚠️  Scripts de debug en directorio raíz: {[f.name for f in debug_files_root]}")
    
    # Archivos de log en múltiples ubicaciones
    log_files = list(project_root.rglob("*.log"))
    if len(log_files) > 1:
        log_locations = [str(f.relative_to(project_root)) for f in log_files]
        warnings.append(f"⚠️  Archivos de log en múltiples ubicaciones: {log_locations}")
    
    # 3. Verificar archivos README
    print("\n📚 Verificando documentación:")
    readme_locations = [
        "README.md",
        "Back-FC/README.md", 
        "Front-FC/README.md",
        "Back-FC/tests/README.md",
        "tools/README.md",
        "docs/PROJECT_STRUCTURE.md"
    ]
    
    for readme in readme_locations:
        full_path = project_root / readme
        if full_path.exists():
            print(f"  ✅ {readme}")
        else:
            warnings.append(f"⚠️  Documentación faltante: {readme}")
    
    # 4. Buscar archivos potencialmente innecesarios
    print("\n🧹 Buscando archivos potencialmente innecesarios:")
    
    # Archivos de respaldo
    backup_files = list(project_root.rglob("*.bak")) + list(project_root.rglob("*.backup"))
    if backup_files:
        warnings.append(f"⚠️  Archivos de respaldo encontrados: {[f.name for f in backup_files]}")
    
    # Archivos temporales de Python
    pyc_files = list(project_root.rglob("*.pyc"))
    if pyc_files:
        warnings.append(f"⚠️  Archivos .pyc encontrados (limpiar cache): {len(pyc_files)} archivos")
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*60)
    
    if not issues and not warnings:
        print("🎉 ¡Estructura del proyecto perfecta!")
    else:
        if issues:
            print("\n🚨 PROBLEMAS CRÍTICOS:")
            for issue in issues:
                print(f"  {issue}")
        
        if warnings:
            print(f"\n⚠️  ADVERTENCIAS ({len(warnings)}):")
            for warning in warnings:
                print(f"  {warning}")
    
    print(f"\n✅ Verificación completada")
    return len(issues) == 0

if __name__ == "__main__":
    success = check_project_structure()
    exit(0 if success else 1)